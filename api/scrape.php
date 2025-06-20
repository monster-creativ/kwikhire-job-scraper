<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 0); // Disable error display in production
ini_set('log_errors', 1);
ini_set('error_log', '/var/www/vhosts/thenewconcept.co.za/httpdocs/kwikhire/logs/php_errors.log');

// Set headers
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.kwikhire.co.za');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Log the start of the request
error_log("Scrape request started");

try {
    // Get POST data
    $json = file_get_contents('php://input');
    error_log("Received raw input: " . $json);

    if (empty($json)) {
        throw new Exception('No data received');
    }

    $data = json_decode($json, true);
    error_log("Decoded data: " . print_r($data, true));

    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('Invalid JSON: ' . json_last_error_msg());
    }

    // Validate input
    if (!isset($data['jobBoard']) || !isset($data['location'])) {
        throw new Exception('Missing required parameters: jobBoard and location are required');
    }

    // Get the absolute path to the job_scraper directory
    $baseDir = '/var/www/vhosts/thenewconcept.co.za/httpdocs/kwikhire/job_scraper';
    error_log("Base directory: " . $baseDir);

    if (!is_dir($baseDir)) {
        throw new Exception("Base directory not found: " . $baseDir);
    }

    // Create results directory if it doesn't exist
    $resultsDir = $baseDir . '/results';
    error_log("Results directory: " . $resultsDir);

    if (!file_exists($resultsDir)) {
        error_log("Creating results directory: " . $resultsDir);
        if (!@mkdir($resultsDir, 0755, true)) {
            $error = error_get_last();
            throw new Exception("Failed to create results directory: " . $resultsDir . " - " . ($error ? $error['message'] : 'Unknown error'));
        }
    }

    // Check if results directory is writable
    if (!is_writable($resultsDir)) {
        throw new Exception("Results directory is not writable: " . $resultsDir);
    }

    // Generate timestamp for filenames
    $timestamp = date('Y-m-d_H-i-s');
    $csvFile = "jobs_{$timestamp}.csv";
    $jsonFile = "jobs_{$timestamp}.json";

    // Build the Python command
    $pythonScript = $baseDir . '/scrape_jobs.py';
    
    // Check if Python script exists and is executable
    if (!file_exists($pythonScript)) {
        throw new Exception("Python script not found: " . $pythonScript);
    }
    
    if (!is_executable($pythonScript)) {
        error_log("Making Python script executable: " . $pythonScript);
        chmod($pythonScript, 0755);
    }

    // Build command with full paths
    $command = sprintf(
        'python3 %s --job-board %s --location "%s" --output-dir %s --csv-filename %s --json-filename %s',
        escapeshellarg($pythonScript),
        escapeshellarg($data['jobBoard']),
        escapeshellarg($data['location']),
        escapeshellarg($resultsDir),
        escapeshellarg($csvFile),
        escapeshellarg($jsonFile)
    );

    // Add keywords if provided
    if (!empty($data['keywords'])) {
        $command .= ' --keywords ' . escapeshellarg($data['keywords']);
    }

    error_log("Executing command: " . $command);

    // Execute the Python script with full environment
    $env = array(
        'PATH' => '/usr/local/bin:/usr/bin:/bin',
        'PYTHONPATH' => $baseDir,
        'HOME' => '/var/www/vhosts/thenewconcept.co.za/httpdocs/kwikhire'
    );
    
    $descriptorspec = array(
        0 => array("pipe", "r"),  // stdin
        1 => array("pipe", "w"),  // stdout
        2 => array("pipe", "w")   // stderr
    );

    $process = proc_open($command, $descriptorspec, $pipes, $baseDir, $env);

    if (is_resource($process)) {
        // Close stdin
        fclose($pipes[0]);

        // Get stdout and stderr
        $output = stream_get_contents($pipes[1]);
        $errors = stream_get_contents($pipes[2]);

        // Close pipes
        fclose($pipes[1]);
        fclose($pipes[2]);

        // Get return value
        $returnVar = proc_close($process);

        error_log("Command output: " . $output);
        error_log("Command errors: " . $errors);
        error_log("Return value: " . $returnVar);

        if ($returnVar !== 0) {
            throw new Exception("Python script failed: " . $errors);
        }
    } else {
        throw new Exception("Failed to execute Python script");
    }

    // Read the JSON output from the Python script
    $jsonPath = $resultsDir . '/' . $jsonFile;
    if (!file_exists($jsonPath)) {
        throw new Exception("JSON file not found: " . $jsonPath . "\nCommand output: " . $output . "\nErrors: " . $errors);
    }

    $jsonContent = file_get_contents($jsonPath);
    if ($jsonContent === false) {
        throw new Exception("Failed to read JSON file: " . $jsonPath);
    }

    $jobs = json_decode($jsonContent, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("Invalid JSON in output file: " . json_last_error_msg());
    }

    // Return success response
    echo json_encode([
        'success' => true,
        'message' => 'Scraping completed successfully',
        'data' => [
            'total_jobs' => count($jobs),
            'csv_file' => 'results/' . $csvFile,
            'json_file' => 'results/' . $jsonFile,
            'jobs' => $jobs
        ]
    ]);

} catch (Exception $e) {
    error_log("Error in scrape.php: " . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?> 