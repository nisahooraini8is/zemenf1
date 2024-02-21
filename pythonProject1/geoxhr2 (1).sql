-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 17, 2023 at 02:28 PM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `geoxhr2`
--

-- --------------------------------------------------------

--
-- Table structure for table `allforms_data`
--

CREATE TABLE `allforms_data` (
  `id` int(11) NOT NULL,
  `form_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `filledby` varchar(250) CHARACTER SET utf8 NOT NULL,
  `belongsto` varchar(250) CHARACTER SET utf8 DEFAULT NULL,
  `form_type` varchar(250) CHARACTER SET utf8 NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(500) COLLATE utf8_bin NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `allforms_data`
--

INSERT INTO `allforms_data` (`id`, `form_id`, `user_id`, `filledby`, `belongsto`, `form_type`, `created_at`, `updated_at`, `status`) VALUES
(1, 1, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-17 15:29:23', '2023-10-17 15:29:23', 'New deal opened and contract signed'),
(2, 2, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-17 15:30:02', '2023-10-17 15:30:02', 'New deal and contract not signed'),
(3, 3, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-17 15:30:30', '2023-10-17 15:30:30', 'Reopened deals'),
(4, 4, 1, 'Geox hr', 'nisa', 'New Deals Contract Signed', '2023-10-17 15:31:05', '2023-10-17 15:31:05', 'New deal opened and contract signed'),
(5, 5, 1, 'Geox hr', 'nisa', 'New Deals Contract Signed', '2023-10-15 15:31:48', '2023-10-15 15:31:48', 'Reopened deals'),
(6, 6, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-17 15:32:15', '2023-10-17 15:32:15', 'Reopened deals'),
(7, 7, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-16 15:33:18', '2023-10-16 15:33:18', 'New deal opened and contract signed'),
(8, 8, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-17 15:56:27', '2023-10-17 15:56:27', 'New deal opened and contract signed'),
(9, 9, 1, 'Geox hr', 'nisa hoorain', 'New Deals Contract Signed', '2023-10-16 16:03:10', '2023-10-16 16:03:10', 'New deal opened and contract signed'),
(10, 10, 1, 'Geox hr', 'hafsa testing', 'New Deals Contract Signed', '2023-10-15 16:04:22', '2023-10-15 16:04:22', 'New deal and contract not signed'),
(11, 11, 1, 'Geox hr', 'nisa', 'New Deals Contract Signed', '2023-10-16 16:05:52', '2023-10-16 16:05:52', 'Reopened deals');

-- --------------------------------------------------------

--
-- Table structure for table `emails_data`
--

CREATE TABLE `emails_data` (
  `id` int(11) NOT NULL,
  `sender_name` varchar(500) NOT NULL,
  `email` varchar(500) DEFAULT NULL,
  `subject_part1` varchar(500) NOT NULL,
  `subject_part2` varchar(500) NOT NULL,
  `formatted_date` varchar(500) NOT NULL,
  `file_name` varchar(500) NOT NULL,
  `file_content` longblob DEFAULT NULL,
  `pdf_content_json` longtext DEFAULT NULL,
  `phone_number` varchar(500) DEFAULT NULL,
  `action` varchar(500) NOT NULL DEFAULT 'user',
  `status` varchar(500) NOT NULL DEFAULT 'applied',
  `is_read` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `hrforms`
--

CREATE TABLE `hrforms` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `candidate_name` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `late` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `informed` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `otherreport` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `reason_vacation` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `notes` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `joborder`
--

CREATE TABLE `joborder` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `title` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payrate` int(11) NOT NULL,
  `salarytype` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `starttime` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `endtime` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vacancy` int(11) NOT NULL,
  `archived` tinyint(1) NOT NULL DEFAULT 0,
  `jobstatus` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `days` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `joborder`
--

INSERT INTO `joborder` (`id`, `user_id`, `company_id`, `title`, `payrate`, `salarytype`, `starttime`, `endtime`, `vacancy`, `archived`, `jobstatus`, `created_at`, `updated_at`, `days`) VALUES
(1, 1, 1, 'python developer', 20, 'Hourly', '19:29', '10:29', 2, 0, 'active', '2023-10-17 15:29:23', '2023-10-17 15:29:23', 'fri, sat, sun'),
(2, 1, 2, 'Driver', 20, 'Hourly', '07:32', '10:29', 2, 0, 'active', '2023-10-17 15:30:02', '2023-10-17 15:30:02', 'thur, fri'),
(3, 1, 3, 'python developer', 10, 'Hourly', '19:32', '11:30', 1, 0, 'active', '2023-10-17 15:30:30', '2023-10-17 15:30:30', 'fri, sat, sun'),
(4, 1, 4, 'Driver', 20, 'Hourly', '07:33', '11:30', 2, 0, 'active', '2023-10-17 15:31:05', '2023-10-17 15:31:05', 'sat, sun'),
(5, 1, 5, 'python developer', 20, 'Hourly', '19:31', '07:33', 1, 0, 'active', '2023-10-17 15:31:48', '2023-10-17 15:31:48', 'sat, sun'),
(6, 1, 6, 'Driver', 20, 'Monthly', '07:36', '10:32', 2, 0, 'active', '2023-10-17 15:32:15', '2023-10-17 15:32:15', 'fri, sat, sun'),
(7, 1, 7, 'python developer', 20, 'Hourly', '07:37', '11:33', 2, 0, 'active', '2023-10-17 15:33:18', '2023-10-17 15:33:18', 'fri, sat'),
(8, 1, 8, 'python developer', 20, 'Hourly', '19:58', '07:59', 2, 0, 'active', '2023-10-17 15:56:27', '2023-10-17 15:56:27', 'sat, sun'),
(9, 1, 9, 'Driver', 20, 'Hourly', '08:06', '08:07', 2, 0, 'active', '2023-10-17 16:03:10', '2023-10-17 16:03:10', 'fri, sat, sun'),
(10, 1, 10, 'python developer', 20, 'Hourly', '08:10', '00:04', 4, 0, 'active', '2023-10-17 16:04:22', '2023-10-17 16:04:22', 'sat, sun'),
(11, 1, 11, 'python developer', 20, 'Hourly', '08:09', '01:05', 2, 0, 'active', '2023-10-17 16:05:52', '2023-10-17 16:05:52', 'sat, sun');

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(500) DEFAULT NULL,
  `title` varchar(500) DEFAULT NULL,
  `image` varchar(500) DEFAULT NULL,
  `company` varchar(500) DEFAULT NULL,
  `location` varchar(500) DEFAULT NULL,
  `job_type` varchar(500) DEFAULT NULL,
  `duration` varchar(500) DEFAULT NULL,
  `onsite` varchar(500) DEFAULT NULL,
  `salary_type` varchar(500) DEFAULT NULL,
  `salary` varchar(500) DEFAULT NULL,
  `job_date` varchar(500) DEFAULT NULL,
  `job_status` varchar(500) DEFAULT NULL,
  `description` varchar(700) DEFAULT NULL,
  `responsibility` varchar(700) DEFAULT NULL,
  `eligibility` varchar(700) DEFAULT NULL,
  `notes` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `marketing`
--

CREATE TABLE `marketing` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `company` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `status` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `cperson` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `cphone` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `location` varchar(500) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `Markup` int(11) NOT NULL,
  `otherReport` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `company_status` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT 'active',
  `notes` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `marketing`
--

INSERT INTO `marketing` (`id`, `user_id`, `name`, `company`, `status`, `cperson`, `cphone`, `location`, `Markup`, `otherReport`, `company_status`, `notes`, `created_at`, `updated_at`) VALUES
(1, 1, 'Geox hr', 'y8hr', 'New deal opened and contract signed', 'nisa hoorain', '12345678910', 'karachi', 10, 'Other report', 'active', 'Other report', '2023-10-17 15:29:23', '2023-10-17 15:29:23'),
(2, 1, 'Geox hr', 'y8hr', 'New deal and contract not signed', 'nisa hoorain', '12345678910', 'karachi', 20, '', 'active', '', '2023-10-17 15:30:02', '2023-10-17 15:30:02'),
(3, 1, 'Geox hr', 'infiniti', 'Reopened deals', 'nisa hoorain', '12345678910', 'karachi', 10, '', 'active', '', '2023-10-17 15:30:30', '2023-10-17 15:30:30'),
(4, 1, 'Geox hr', 'nisacompany1', 'New deal opened and contract signed', 'nisa', '1561654135', 'karachi', 200, '', 'active', '', '2023-10-17 15:31:05', '2023-10-17 15:31:05'),
(5, 1, 'Geox hr', 'nisacompany2', 'Reopened deals', 'nisa', '1561654135', 'karachi', 10, '', 'active', '', '2023-10-15 15:31:48', '2023-10-15 15:31:48'),
(6, 1, 'Geox hr', 'y8hr', 'Reopened deals', 'nisa hoorain', '12345678910', 'karachi', 10, '', 'active', '', '2023-10-17 15:32:15', '2023-10-17 15:32:15'),
(7, 1, 'Geox hr', 'y8hr', 'New deal opened and contract signed', 'nisa hoorain', '12345678910', 'karachi', 10, '', 'active', '', '2023-10-16 15:33:18', '2023-10-16 15:33:18'),
(8, 1, 'Geox hr', 'y8hr', 'New deal opened and contract signed', 'nisa hoorain', '12345678910', 'karachi', 10, '', 'active', '', '2023-10-17 15:56:27', '2023-10-17 15:56:27'),
(9, 1, 'Geox hr', 'newcompany', 'New deal opened and contract signed', 'nisa hoorain', '12345678910', 'karachi', 100, '', 'active', '', '2023-10-16 16:03:10', '2023-10-16 16:03:10'),
(10, 1, 'Geox hr', 'testing company hafsa', 'New deal and contract not signed', 'hafsa testing', '07489738923', 'karachi', 10, '', 'active', '', '2023-10-15 16:04:22', '2023-10-15 16:04:22'),
(11, 1, 'Geox hr', 'nisacompany', 'Reopened deals', 'nisa', '1561654135', 'karachi', 10, '', 'active', '', '2023-10-16 16:05:52', '2023-10-16 16:05:52');

-- --------------------------------------------------------

--
-- Table structure for table `otherfinal`
--

CREATE TABLE `otherfinal` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(250) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `other_report` varchar(500) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `notes` varchar(700) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `recruiting_data`
--

CREATE TABLE `recruiting_data` (
  `id` int(11) NOT NULL,
  `user_id` varchar(250) NOT NULL,
  `name` varchar(500) DEFAULT NULL,
  `candidate` varchar(500) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `company` varchar(500) DEFAULT NULL,
  `did_you` varchar(500) DEFAULT NULL,
  `ecname` varchar(500) DEFAULT NULL,
  `ecnumber` varchar(20) DEFAULT NULL,
  `location` varchar(500) DEFAULT NULL,
  `locationcgoing` varchar(500) DEFAULT NULL,
  `starttime` varchar(500) DEFAULT NULL,
  `needmember` varchar(500) DEFAULT NULL,
  `photo` varchar(500) DEFAULT NULL,
  `interviewdate` varchar(500) DEFAULT NULL,
  `companydate` varchar(500) DEFAULT NULL,
  `help` varchar(500) DEFAULT NULL,
  `person_starting` varchar(500) DEFAULT NULL,
  `other_report` varchar(500) DEFAULT NULL,
  `position` varchar(500) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `role_name` varchar(250) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`id`, `role_name`) VALUES
(1, 'admin'),
(2, 'user');

-- --------------------------------------------------------

--
-- Table structure for table `userdesignation_data`
--

CREATE TABLE `userdesignation_data` (
  `id` int(11) NOT NULL,
  `designation` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `userdesignation_data`
--

INSERT INTO `userdesignation_data` (`id`, `designation`) VALUES
(1, 'admin'),
(2, 'manager'),
(3, 'caller'),
(4, 'recruiter');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `role` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `fname` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `lname` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(700) COLLATE utf8_unicode_ci NOT NULL,
  `designation` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `role`, `fname`, `lname`, `email`, `password`, `designation`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'Geox', 'hr', 'admin@gmail.com', '$5$rounds=535000$LoQFSlpGesGVMsvo$opTSCzmPRLBgJ2bT5fi.gyMyshrRvuyI6/NvMwuLOG2', 'admin', '2023-09-12 13:19:43', '2023-09-12 13:19:43'),
(3, 'user', 'Mahira', 'Mehtab', 'mahira@geoxhr.com', '$5$rounds=535000$cz8ttYMFfIujrZBh$39jvKSEhpPHuD/EWj1DrGERrP7pfzwnfUV/2hqjGmwB', 'recruiter', '2023-09-12 19:21:40', '2023-09-12 13:21:39'),
(4, 'user', 'Kainat', 'Ishtiaq', 'kainat@geoxhr.com', '$5$rounds=535000$Q2zdGWmpyuMzzYvf$g04WUsh2aiCYcIpHoBKCOs/cDZf6fvMnXmtWUo2d58D', 'recruiter', '2023-09-12 19:22:17', '2023-09-12 13:22:16'),
(5, 'user', 'Neeraj', 'Goyal', 'neeraj@geoxhr.com', '$5$rounds=535000$gYFfffEYOBIO1aA2$2U.D4I1EtnPliflTLdZE3ZfOkwAZwzfTntQTPjEkE68', 'manager', '2023-09-12 19:23:12', '2023-09-12 13:23:11'),
(6, 'user', 'Jonah', 'M.', 'jonah@geoxhr.com', '$5$rounds=535000$s/5WALqd91SKCTn5$o6Xrbtm/uegdyFwEmr8MRMFdgM4FUIOlpL95Xyw0dJ1', 'caller', '2023-09-12 19:24:08', '2023-09-12 13:24:07'),
(7, 'user', 'Sy', 'Caps', 'sy@geoxhr.com', '$5$rounds=535000$eK16oHlDclfPhHYz$y9Ig47LAKLjNJAaNwkADB07jxg0UHxLprYvrjwBf0o8', 'caller', '2023-09-12 19:24:45', '2023-09-12 13:24:45'),
(8, 'user', 'Kinza', 'Khan', 'kinza@geoxhr.com', '$5$rounds=535000$SAMTDaI6G5nHwPtE$StXhVW0t2dnwoJlOV2jjoR5QdKjZGE1wz5zPkzTgnd3', 'recruiter', '2023-09-12 19:25:20', '2023-09-12 13:25:19'),
(9, 'user', 'Uroosa', 'Iqbal', 'uroosa@geoxhr.com', '$5$rounds=535000$wqtfPWAizHC4Oove$uxZtXaANxDsRPXjnnaV9HsUJScJix3Omh//wn7Qqp4A', 'recruiter', '2023-09-12 19:26:28', '2023-09-12 13:26:27'),
(12, 'user', 'Qareena', 'K.', 'qk@geoxhr.com', '$5$rounds=535000$.zxfW862jwGkAioD$xVUAC8aTlvC1PQKfzaKe8K4iAPuc9PYSBKGzVGDGFPB', 'manager', '2023-09-12 20:37:53', '2023-09-12 14:37:53'),
(15, 'user', 'Sandeep ', 'Kaur ', 'sandeep@geoxhr.com', '$5$rounds=535000$kirgNaJa.eT/Yr5q$EYRwljwjKmjNJgcDSdnWdSx7u3oV/aiHSYVSivpDra6', 'caller', '2023-10-02 23:54:51', '2023-10-02 23:54:50'),
(18, 'user', 'Zainab', 'Gull', 'zainab@geoxhr.com', '$5$rounds=535000$NQj01GWbU2ADyASu$OOQpFirt//Qngnu8Htj2FWKMB030Yi/Sx0bJHQBBCx9', 'recruiter', '2023-10-03 22:08:23', '2023-10-03 22:08:22');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `allforms_data`
--
ALTER TABLE `allforms_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `emails_data`
--
ALTER TABLE `emails_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hrforms`
--
ALTER TABLE `hrforms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `joborder`
--
ALTER TABLE `joborder`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `marketing`
--
ALTER TABLE `marketing`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `otherfinal`
--
ALTER TABLE `otherfinal`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `recruiting_data`
--
ALTER TABLE `recruiting_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `userdesignation_data`
--
ALTER TABLE `userdesignation_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `allforms_data`
--
ALTER TABLE `allforms_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `emails_data`
--
ALTER TABLE `emails_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hrforms`
--
ALTER TABLE `hrforms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `joborder`
--
ALTER TABLE `joborder`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `marketing`
--
ALTER TABLE `marketing`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `otherfinal`
--
ALTER TABLE `otherfinal`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `recruiting_data`
--
ALTER TABLE `recruiting_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `role`
--
ALTER TABLE `role`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `userdesignation_data`
--
ALTER TABLE `userdesignation_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
