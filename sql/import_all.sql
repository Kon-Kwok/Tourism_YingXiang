
-- =========================================
-- import_all.sql
-- 一键导入所有表
-- 执行顺序: 01_init -&gt; 03_data_batch -&gt; 02_biz_tables
-- =========================================

-- 1. 创建数据库
SOURCE sql/01_init/01_create_database.sql;

-- 2. 创建批次表
SOURCE sql/03_data_batch/spider_data_batch.sql;

-- 3. 创建业务表
SOURCE sql/02_biz_tables/biz_customer_service_daily.sql;
SOURCE sql/02_biz_tables/biz_customer_service_weekly.sql;
SOURCE sql/02_biz_tables/biz_cs_workload_log.sql;
SOURCE sql/02_biz_tables/biz_agent_performance_daily.sql;
SOURCE sql/02_biz_tables/biz_agent_sales_daily.sql;
SOURCE sql/02_biz_tables/biz_fliggy_store_daily.sql;
SOURCE sql/02_biz_tables/biz_fliggy_order_daily.sql;

SELECT '数据库初始化完成！' AS message;

