-- =========================================
-- 一键导入所有Excel表格对应的MySQL表
-- =========================================

-- 注意：确保数据库 xiangwang_fliggy_system 已经创建
-- 如未创建，请先执行: CREATE DATABASE xiangwang_fliggy_system;

USE xiangwang_fliggy_system;

-- 千牛数据表
SOURCE sql/千牛/店铺数据每日登记/店铺数据每日登记.sql;
SOURCE sql/千牛/飞猪店铺日度关键数据/飞猪店铺日度关键数据.sql;

-- 飞猪数据表
SOURCE sql/飞猪/万相台/万相台.sql;
SOURCE sql/飞猪/客服数据汇总-周数据/客服数据汇总-周数据.sql;
SOURCE sql/飞猪/客服数据汇总-日数据/客服数据汇总-日数据.sql;
SOURCE sql/飞猪/客服绩效-工作量分析/客服绩效-工作量分析.sql;
SOURCE sql/飞猪/客服绩效-汇总/客服绩效-汇总.sql;
SOURCE sql/飞猪/引力魔方/引力魔方.sql;
SOURCE sql/飞猪/明星店铺/明星店铺.sql;
SOURCE sql/飞猪/直通车/直通车.sql;

-- 显示创建的所有表
SELECT CONCAT('已创建 ', COUNT(*), ' 个Excel对应表') AS message
FROM information_schema.tables
WHERE table_schema = 'xiangwang_fliggy_system'
AND table_name IN (
    'qianniu_shop_data_daily_registration',
    'qianniu_fliggy_shop_daily_key_data',
    'fliggy_wanxiangtai',
    'fliggy_customer_service_data_weekly',
    'fliggy_customer_service_data_daily',
    'fliggy_customer_service_performance_workload_analysis',
    'fliggy_customer_service_performance_summary',
    'fliggy_gravity_rubiks_cube',
    'fliggy_star_store',
    'fliggy_tmall_express'
);
