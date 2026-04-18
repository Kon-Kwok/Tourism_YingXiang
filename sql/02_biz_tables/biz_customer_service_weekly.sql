
-- =========================================
-- biz_customer_service_weekly.sql
-- 客服数据周报表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_customer_service_weekly (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    stat_week VARCHAR(50) NOT NULL COMMENT '统计周',
    customer_service VARCHAR(100) COMMENT '客服姓名',
    incoming_count INT COMMENT '接入人数',
    avg_response_time_sec DECIMAL(8,2) COMMENT '平均响应时间(秒)',
    complaint_count INT COMMENT '差评数',
    consult_to_booking_success_rate DECIMAL(5,4) COMMENT '咨询-&gt;预订成功率',
    offline_count INT COMMENT '离线次数',
    complaint_review_count INT COMMENT '差评复核数',
    customer_satisfaction_score DECIMAL(5,2) COMMENT '客户满意度',
    transfer_count INT COMMENT '转接数',
    hangup_count INT COMMENT '挂起数',
    first_response_count INT COMMENT '首次响应数',
    supplement_count INT COMMENT '补充数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_week (stat_week),
    INDEX idx_customer_service (customer_service),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客服数据周报表';

