<?php
// Connection to MySQL
$servername = "localhost";
$username = "your_db_username";
$password = "your_db_password";
$dbname = "your_database_name";

// Create connection - mysqli is provided by php for database interaction
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection - $conn->connect_error contains the error message
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form inputs
    $name = $_POST['name'];
    $gender = $_POST['gender'];
    $age = $_POST['age'];
    $address = $_POST['address'];
    $email = $_POST['email'];
    $username = $_POST['signup-username'];
    $password = $_POST['signup-password'];
    $confirm_password = $_POST['confirm-password'];

    // Check if passwords match
    if ($password !== $confirm_password) {
        echo "Passwords do not match!";
        exit;
    }

    // Hash the password
    $hashed_password = password_hash($password, PASSWORD_BCRYPT);   //PASSWORD_BCRYPT is a hashing algo

    // Prepare SQL statement
    $stmt = $conn->prepare("INSERT INTO users (name, gender, age, address, email, username, password1) VALUES (?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssissss", $name, $gender, $age, $address, $email, $username, $hashed_password);

    // Execute the statement
    if ($stmt->execute()) {
        echo "Signup successful!";
        header("Location: login.html");
    } else {
        error_log("Database error: " . $stmt->error); // Log error
        echo "Error: " . $stmt->error;
    }

    // Close connections
    $stmt->close();
    $conn->close();
}
?>
