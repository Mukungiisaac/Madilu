<?php
/**
 * Database Connection Configuration
 */

$db_host = 'localhost';
$db_name = 'itech_events';
$db_user = 'root';
$db_pass = ''; // Your MySQL password if any

try {
    // Create PDO connection
    $pdo = new PDO(
        "mysql:host={$db_host};dbname={$db_name};charset=utf8mb4",
        $db_user,
        $db_pass,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false
        ]
    );
    
    // Set timezone
    $pdo->exec("SET time_zone = '+03:00'");
    
} catch (PDOException $e) {
    // Log error (don't show to users in production)
    error_log("Database Connection Error: " . $e->getMessage());
    
    // For development - show error
    die("Connection failed: " . $e->getMessage());
}

/**
 * Helper function to generate booking reference
 */
function generateBookingReference() {
    return 'ITECH-' . strtoupper(substr(md5(uniqid(rand(), true)), 0, 6));
}

/**
 * Helper function to format price
 */
function formatPrice($price) {
    return 'KSh ' . number_format($price, 0, '.', ',');
}

/**
 * Close connection (optional - PDO closes automatically)
 */
function closeConnection() {
    $pdo = null;
}
