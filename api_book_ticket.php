<?php
/**
 * API - Book Ticket
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

require_once 'db_connection.php';

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Validate required fields
        $required = ['eventId', 'fullName', 'email', 'phone', 'idNumber', 'standardQty', 'vipQty'];
        foreach ($required as $field) {
            if (!isset($data[$field]) && $field !== 'standardQty' && $field !== 'vipQty') {
                throw new Exception("Missing required field: {$field}");
            }
        }
        
        $eventId = (int)$data['eventId'];
        $fullName = trim($data['fullName']);
        $email = trim($data['email']);
        $phone = trim($data['phone']);
        $idNumber = trim($data['idNumber']);
        $standardQty = (int)($data['standardQty'] ?? 0);
        $vipQty = (int)($data['vipQty'] ?? 0);
        
        // Validate at least one ticket
        if ($standardQty === 0 && $vipQty === 0) {
            throw new Exception("Please select at least one ticket");
        }
        
        // Get event details
        $stmt = $pdo->prepare("SELECT * FROM events WHERE id = ? AND status = 'published'");
        $stmt->execute([$eventId]);
        $event = $stmt->fetch();
        
        if (!$event) {
            throw new Exception("Event not found or not available");
        }
        
        // Calculate total
        $total = ($standardQty * $event['standard_price']) + ($vipQty * $event['vip_price']);
        
        // Generate booking reference
        $bookingRef = generateBookingReference();
        
        // Begin transaction
        $pdo->beginTransaction();
        
        // Check if user exists, if not create them
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);
        $user = $stmt->fetch();
        
        if (!$user) {
            $stmt = $pdo->prepare("INSERT INTO users (full_name, email, phone, id_number, user_type) VALUES (?, ?, ?, ?, 'customer')");
            $stmt->execute([$fullName, $email, $phone, $idNumber]);
            $userId = $pdo->lastInsertId();
        } else {
            $userId = $user['id'];
        }
        
        // Create booking
        $stmt = $pdo->prepare("
            INSERT INTO bookings (user_id, event_id, booking_reference, full_name, email, phone, id_number, total_amount, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ");
        $stmt->execute([$userId, $eventId, $bookingRef, $fullName, $email, $phone, $idNumber, $total]);
        $bookingId = $pdo->lastInsertId();
        
        // Insert ticket details
        if ($standardQty > 0) {
            // Get or create standard ticket type
            $stmt = $pdo->prepare("SELECT id FROM ticket_types WHERE event_id = ? AND type_name = 'standard'");
            $stmt->execute([$eventId]);
            $ticketType = $stmt->fetch();
            
            if (!$ticketType) {
                $stmt = $pdo->prepare("INSERT INTO ticket_types (event_id, type_name, price, available_quantity) VALUES (?, 'standard', ?, 1000)");
                $stmt->execute([$eventId, $event['standard_price']]);
                $ticketTypeId = $pdo->lastInsertId();
            } else {
                $ticketTypeId = $ticketType['id'];
            }
            
            $stmt = $pdo->prepare("
                INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ");
            $stmt->execute([$bookingId, $ticketTypeId, $standardQty, $event['standard_price'], $standardQty * $event['standard_price']]);
            
            // Update sold quantity
            $stmt = $pdo->prepare("UPDATE ticket_types SET sold_quantity = sold_quantity + ? WHERE id = ?");
            $stmt->execute([$standardQty, $ticketTypeId]);
        }
        
        if ($vipQty > 0) {
            // Get or create VIP ticket type
            $stmt = $pdo->prepare("SELECT id FROM ticket_types WHERE event_id = ? AND type_name = 'vip'");
            $stmt->execute([$eventId]);
            $ticketType = $stmt->fetch();
            
            if (!$ticketType) {
                $stmt = $pdo->prepare("INSERT INTO ticket_types (event_id, type_name, price, available_quantity) VALUES (?, 'vip', ?, 100)");
                $stmt->execute([$eventId, $event['vip_price']]);
                $ticketTypeId = $pdo->lastInsertId();
            } else {
                $ticketTypeId = $ticketType['id'];
            }
            
            $stmt = $pdo->prepare("
                INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ");
            $stmt->execute([$bookingId, $ticketTypeId, $vipQty, $event['vip_price'], $vipQty * $event['vip_price']]);
            
            // Update sold quantity
            $stmt = $pdo->prepare("UPDATE ticket_types SET sold_quantity = sold_quantity + ? WHERE id = ?");
            $stmt->execute([$vipQty, $ticketTypeId]);
        }
        
        // Commit transaction
        $pdo->commit();
        
        // Return success
        echo json_encode([
            'success' => true,
            'message' => 'Booking created successfully',
            'data' => [
                'bookingReference' => $bookingRef,
                'totalAmount' => $total,
                'eventTitle' => $event['title'],
                'eventDate' => $event['event_date'],
                'tickets' => [
                    'standard' => $standardQty,
                    'vip' => $vipQty
                ]
            ]
        ]);
        
    } catch (Exception $e) {
        if (isset($pdo) && $pdo->inTransaction()) {
            $pdo->rollBack();
        }
        
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => $e->getMessage()
        ]);
    }
} else {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => 'Method not allowed'
    ]);
}
