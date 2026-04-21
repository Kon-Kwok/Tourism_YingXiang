-- =========================================
-- 客服绩效-汇总
-- 文件: 客服绩效-汇总.xlsx
-- =========================================
USE feizhu;

CREATE TABLE IF NOT EXISTS fliggy_customer_service_performance_summary (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    旺旺昵称 VARCHAR(100) COMMENT '旺旺昵称',
    咨询人数 INT COMMENT '咨询人数',
    接待人数 INT COMMENT '接待人数',
    询单人数 VARCHAR(20) COMMENT '询单人数',
    销售额 DECIMAL(14,2) COMMENT '销售额',
    销售量 INT COMMENT '销售量',
    销售人数 INT COMMENT '销售人数',
    订单数 INT COMMENT '订单数',
    date_time DATE COMMENT 'Date',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_旺旺昵称 (旺旺昵称),
    INDEX idx_date_time (date_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪客服绩效汇总';
