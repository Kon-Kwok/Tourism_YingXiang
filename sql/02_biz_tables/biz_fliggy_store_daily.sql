
-- =========================================
-- biz_fliggy_store_daily.sql
-- 飞猪店铺每日关键数据表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_fliggy_store_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    stat_date DATE NOT NULL COMMENT '统计日期',
    total_pv BIGINT COMMENT 'Total PV',
    total_uv BIGINT COMMENT 'Total UV',
    free_source_uv BIGINT COMMENT '免费来源UV',
    platform_source_uv BIGINT COMMENT '平台来源UV',
    direct_product_uv BIGINT COMMENT '直达商品UV',
    chat_volume INT COMMENT 'Chat Volume',
    total_bookings INT COMMENT 'Total Bookings',
    total_pax INT COMMENT 'Total PAX',
    gmv DECIMAL(14,2) COMMENT 'GMV',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_date (stat_date),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪店铺每日关键数据表';

