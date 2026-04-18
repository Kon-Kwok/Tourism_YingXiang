
-- =========================================
-- spider_data_batch.sql
-- 数据采集批次表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS spider_data_batch (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    page_id VARCHAR(100) NOT NULL COMMENT '页面ID(对应JSON配置)',
    page_name VARCHAR(200) COMMENT '页面名称',
    batch_start_time TIMESTAMP NULL COMMENT '采集开始时间',
    batch_end_time TIMESTAMP NULL COMMENT '采集结束时间',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/running/success/failed',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_page_id (page_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据采集批次表';

