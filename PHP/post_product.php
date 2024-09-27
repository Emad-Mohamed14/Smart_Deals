<?php
// Include your database connection file
include 'db_connection.php';

session_start(); // Assuming you have user sessions set up
$owner_id = $_SESSION['user_id']; // Capture the user's ID from the session

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Collect form data
    $product_name = $_POST['product_name'];
    $category = $_POST['category'];
    $product_description = $_POST['product_description'];
    $rating = $_POST['rating'];
    $purchase_date = $_POST['purchase_date'];
    $cost_price = $_POST['cost_price'];
    $selling_price = $_POST['selling_price'];

    // Handle image upload and store its path
    $target_dir = "uploads/";
    $target_file = $target_dir . basename($_FILES["image"]["name"]);
    $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
    
    // Move uploaded file to server
    move_uploaded_file($_FILES["image"]["tmp_name"], $target_file);

    // Insert product details into the database
    $sql = "INSERT INTO products (product_name, category, product_description, image_url, rating, purchase_date, cost_price, selling_price, owner_id)
            VALUES ('$product_name', '$category', '$product_description', '$target_file', '$rating', '$purchase_date', '$cost_price', '$selling_price', '$owner_id')";

    if ($conn->query($sql) === TRUE) {
        echo "Product posted successfully!";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }

    // Close the database connection
    $conn->close();
}
?>
