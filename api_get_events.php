<?php
/**
 * API - Get Events
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

require_once 'db_connection.php';

try {
    $stmt = $pdo->prepare("
        SELECT e.*, v.name as venue_name, v.address, v.city,
               (SELECT COUNT(*) FROM ticket_types WHERE event_id = e.id AND sold_quantity < available_quantity) as available_tickets
        FROM events e
        JOIN venues v ON e.venue_id = v.id
        WHERE e.status = 'published' AND e.event_date >= NOW()
        ORDER BY e.event_date ASC
    ");
    $stmt->execute();
    $events = $stmt->fetchAll();
    
    // Format prices
    foreach ($events as &$event) {
        $event['standard_price_formatted'] = formatPrice($event['standard_price']);
        $event['vip_price_formatted'] = formatPrice($event['vip_price']);
        $event['event_date_formatted'] = date('M d, Y', strtotime($event['event_date']));
    }
    
    echo json_encode([
        'success' => true,
        'data' => $events
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}
