-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 19, 2024 at 10:30 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `foodtorecipe`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'Test User', 'test@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '2024-12-19 10:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `upload_history`
--

CREATE TABLE `upload_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `food_detected` varchar(100) NOT NULL,
  `score` decimal(5,4) NOT NULL,
  `upload_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--

--

--
-- Table structure for table `recipe_ratings`
-- Stores user ratings and feedback for recipes
--

CREATE TABLE `recipe_ratings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` >= 1 AND `rating` <= 5),
  `feedback_text` text DEFAULT NULL,
  `cooking_experience` enum('easy','medium','hard') DEFAULT 'medium',
  `taste_rating` int(11) DEFAULT NULL CHECK (`taste_rating` >= 1 AND `taste_rating` <= 5),
  `presentation_rating` int(11) DEFAULT NULL CHECK (`presentation_rating` >= 1 AND `presentation_rating` <= 5),
  `would_cook_again` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `recipe_shares`
-- Tracks recipe sharing activities across different platforms
--

CREATE TABLE `recipe_shares` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `share_type` enum('social_media','email','whatsapp','copy_link') NOT NULL,
  `share_data` json DEFAULT NULL,
  `shared_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `recipe_comments`
-- Stores community comments and user feedback
--

CREATE TABLE `recipe_comments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `comment_text` text NOT NULL,
  `is_public` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `recipe_favorites`
-- Manages user's favorite recipes collection
--

CREATE TABLE `recipe_favorites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `upload_history`
--
ALTER TABLE `upload_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `recipe_ratings`
--
ALTER TABLE `recipe_ratings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_recipe` (`user_id`, `food_name`),
  ADD KEY `idx_recipe_ratings_food` (`food_name`),
  ADD KEY `idx_recipe_ratings_user` (`user_id`);

--
-- Indexes for table `recipe_shares`
--
ALTER TABLE `recipe_shares`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_recipe_shares_food` (`food_name`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `recipe_comments`
--
ALTER TABLE `recipe_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_recipe_comments_food` (`food_name`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `recipe_favorites`
--
ALTER TABLE `recipe_favorites`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_favorite` (`user_id`, `food_name`),
  ADD KEY `user_id` (`user_id`);

-- --------------------------------------------------------

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `upload_history`
--
ALTER TABLE `upload_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recipe_ratings`
--
ALTER TABLE `recipe_ratings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recipe_shares`
--
ALTER TABLE `recipe_shares`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recipe_comments`
--
ALTER TABLE `recipe_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recipe_favorites`
--
ALTER TABLE `recipe_favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

-- --------------------------------------------------------

--
-- Constraints for dumped tables
--

--
-- Constraints for table `upload_history`
--
ALTER TABLE `upload_history`
  ADD CONSTRAINT `upload_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recipe_ratings`
--
ALTER TABLE `recipe_ratings`
  ADD CONSTRAINT `recipe_ratings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recipe_shares`
--
ALTER TABLE `recipe_shares`
  ADD CONSTRAINT `recipe_shares_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recipe_comments`
--
ALTER TABLE `recipe_comments`
  ADD CONSTRAINT `recipe_comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recipe_favorites`
--
ALTER TABLE `recipe_favorites`
  ADD CONSTRAINT `recipe_favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- --------------------------------------------------------

--
-- Sample data for testing new features
--

-- Insert sample recipe ratings
INSERT INTO `recipe_ratings` (`user_id`, `food_name`, `rating`, `feedback_text`, `cooking_experience`, `taste_rating`, `presentation_rating`, `would_cook_again`) VALUES
(1, 'pizza', 5, 'Amazing recipe! The crust was perfect and the toppings were delicious.', 'medium', 5, 4, 1),
(1, 'chocolate_cake', 4, 'Great taste but took longer to bake than expected.', 'hard', 5, 3, 1);

-- Insert sample recipe shares
INSERT INTO `recipe_shares` (`user_id`, `food_name`, `share_type`, `share_data`) VALUES
(1, 'pizza', 'social_media', '{"platform": "facebook", "timestamp": "2024-12-19T10:30:00Z"}'),
(1, 'chocolate_cake', 'whatsapp', '{"recipient": "family", "timestamp": "2024-12-19T10:30:00Z"}');

-- Insert sample recipe comments
INSERT INTO `recipe_comments` (`user_id`, `food_name`, `comment_text`, `is_public`) VALUES
(1, 'pizza', 'This recipe is perfect for family dinners!', 1),
(1, 'chocolate_cake', 'I added some vanilla extract and it tasted even better.', 1);

-- Insert sample recipe favorites
INSERT INTO `recipe_favorites` (`user_id`, `food_name`) VALUES
(1, 'pizza'),
(1, 'chocolate_cake');

-- --------------------------------------------------------

--
-- Database Schema Summary for MCA Project Guide
-- =============================================
--
-- This database supports a comprehensive Image2Recipe application with:
--
-- 1. USER MANAGEMENT:
--    - User registration and authentication
--    - Profile management
--
-- 2. CORE FUNCTIONALITY:
--    - Food image upload and analysis
--    - Recipe generation and storage
--    - Upload history tracking
--
-- 3. NEW FEATURES ADDED:
--    - Recipe Rating System (1-5 stars for overall, taste, presentation)
--    - Cooking Experience Classification (Easy/Medium/Hard)
--    - User Feedback and Comments
--    - Social Media Sharing Integration
--    - Personal Favorites Management
--    - Community Engagement Features
--
-- 4. TECHNICAL FEATURES:
--    - Proper foreign key relationships
--    - Performance indexes for scalability
--    - JSON data storage for flexible sharing metadata
--    - Timestamp tracking for all activities
--    - Data integrity constraints
--
-- 5. BUSINESS VALUE:
--    - User engagement through ratings and comments
--    - Social proof and community building
--    - Data analytics capabilities
--    - Scalable architecture for growth
--
-- This schema demonstrates professional database design principles
-- suitable for a major MCA final year project.
--

-- --------------------------------------------------------

--
-- DEBUGGING QUERIES FOR FAVORITES FUNCTIONALITY
-- =============================================
-- Use these queries in phpMyAdmin to troubleshoot favorites issues
--

-- Check if recipe_favorites table exists and has correct structure
USE foodtorecipe;

-- Check if table exists
SHOW TABLES LIKE 'recipe_favorites';

-- Check table structure
DESCRIBE recipe_favorites;

-- Check if there are any records
SELECT COUNT(*) as total_favorites FROM recipe_favorites;

-- Check sample data
SELECT * FROM recipe_favorites LIMIT 5;

-- Check foreign key constraint
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE 
    TABLE_SCHEMA = 'foodtorecipe' 
    AND TABLE_NAME = 'recipe_favorites'
    AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Check if users table has the expected structure
DESCRIBE users;

-- Check sample users
SELECT id, username, email FROM users LIMIT 5;

-- --------------------------------------------------------

--
-- QUICK FIXES FOR COMMON FAVORITES ISSUES
-- =======================================
--

-- If recipe_favorites table is missing, run this:
/*
CREATE TABLE `recipe_favorites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `food_name` varchar(100) NOT NULL,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_favorite` (`user_id`, `food_name`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `recipe_favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
*/

-- If you get user ID errors, check your actual user ID first:
-- SELECT * FROM users;

-- Then update sample data with your actual user ID:
/*
UPDATE recipe_ratings SET user_id = YOUR_USER_ID WHERE user_id = 1;
UPDATE recipe_shares SET user_id = YOUR_USER_ID WHERE user_id = 1;
UPDATE recipe_comments SET user_id = YOUR_USER_ID WHERE user_id = 1;
UPDATE recipe_favorites SET user_id = YOUR_USER_ID WHERE user_id = 1;
*/

-- --------------------------------------------------------

--
-- TROUBLESHOOTING CHECKLIST
-- =========================
--
-- 1. XAMPP MySQL is running ✅
-- 2. foodtorecipe database exists ✅
-- 3. recipe_favorites table exists ✅
-- 4. users table has data ✅
-- 5. You're logged in to the app ✅
-- 6. No JavaScript errors in browser console ✅
-- 7. No Python errors in Flask console ✅
--
-- If any step fails, use the debug queries above to identify the issue.
--

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
