
-- =========================================
-- biz_cs_workload_log.sql
-- 客服工作量分析表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_cs_workload_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    customer_service VARCHAR(100) COMMENT '客服姓名',
    operation_time DATETIME COMMENT '操作时间',
    operation_type VARCHAR(50) COMMENT '操作类型',
    info_source VARCHAR(100) COMMENT '信息来源',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_service (customer_service),
    INDEX idx_operation_time (operation_time),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客服工作量分析表';

