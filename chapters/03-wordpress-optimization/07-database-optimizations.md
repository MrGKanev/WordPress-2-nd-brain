# Database Optimization

## Overview

Database optimization is critical for WordPress performance, especially for sites with heavy admin usage or large amounts of content. A well-optimized database reduces query times, server load, and improves overall site responsiveness.

## Database Cleanup Tools

Several tools are recommended for database maintenance:

| Tool | Purpose | Key Benefits |
|------|---------|-------------|
| **WP-Sweep** | General DB cleaning | Uses proper WordPress delete functions instead of direct SQL queries |
| **Plugins Garbage Collector** | Identify unused DB tables | Finds tables left by uninstalled plugins |
| **Autoload Checker** | Optimize autoloaded options | Reduces memory usage on every page load |
| **AAA Option Optimizer** | Alternative for autoload optimization | Provides visualization of autoloaded data size |

## Critical Database Tables to Monitor

### wp_options Table

The `wp_options` table is loaded on every page request and can significantly impact performance:

```sql
-- Check size of wp_options table
SELECT count(*) FROM wp_options;

-- Check autoloaded data size
SELECT SUM(LENGTH(option_value)) / 1024 / 1024 as 'Autoloaded data in MB' 
FROM wp_options WHERE autoload='yes';

-- Find largest autoloaded options
SELECT option_name, LENGTH(option_value) / 1024 / 1024 as size_in_mb 
FROM wp_options 
WHERE autoload='yes' 
ORDER BY size_in_mb DESC 
LIMIT 20;
```

### wp_postmeta Table

The `wp_postmeta` table often grows excessively large:

```sql
-- Check postmeta table size
SELECT count(*) FROM wp_postmeta;

-- Find orphaned postmeta
SELECT pm.meta_id, pm.post_id, pm.meta_key, pm.meta_value 
FROM wp_postmeta pm 
LEFT JOIN wp_posts p ON p.ID = pm.post_id 
WHERE p.ID IS NULL 
LIMIT 100;
```

## Manual Database Optimization Techniques

Experienced developers perform these optimizations depending on the site’s needs:

### 1. Removing Transients

```sql
-- Delete expired transients
DELETE FROM wp_options WHERE option_name LIKE '%_transient_%' AND autoload='yes';
```

### 2. Post Revisions Management

```php
// Limit post revisions (add to wp-config.php)
define('WP_POST_REVISIONS', 5);

// Delete excess revisions with SQL
DELETE p, pr1, pr2 
FROM wp_posts p 
LEFT JOIN wp_term_relationships pr1 ON p.ID = pr1.object_id 
LEFT JOIN wp_postmeta pr2 ON p.ID = pr2.post_id 
WHERE p.post_type = 'revision' 
AND p.post_parent NOT IN (
  SELECT ID FROM (
    SELECT ID FROM wp_posts WHERE post_type = 'post' OR post_type = 'page'
  ) AS temp
);
```

### 3. Clean Unused Term Relationships

```sql
-- Remove orphaned term relationships
DELETE tr FROM wp_term_relationships tr
LEFT JOIN wp_posts p ON tr.object_id = p.ID
WHERE p.ID IS NULL;
```

## Database Indexing

Proper database indexing is often overlooked:

```sql
-- Add index to postmeta table (example)
ALTER TABLE wp_postmeta ADD INDEX meta_value (meta_value(32));
```

> **Expert insight**: "Even vanilla WordPress installations can benefit from additional database indexes. Tools like Index MySQL for Speed and Scalability Pro add necessary indexes that improve query performance."

## Implementation Steps

1. **Backup the database** before performing any optimization
2. **Start with plugin-based cleanup** using WP-Sweep
3. **Identify autoloaded data issues** with Autoload Checker
4. **Remove orphaned data** from plugin tables
5. **Add indexes** to frequently queried columns
6. **Set up regular maintenance** tasks via cron jobs
