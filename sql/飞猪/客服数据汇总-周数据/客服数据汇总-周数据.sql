-- =========================================
-- 客服数据汇总-周数据
-- 文件: 客服数据汇总-周数据.xlsx
-- =========================================
USE feizhu;

CREATE TABLE IF NOT EXISTS fliggy_customer_service_data_weekly (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    日期 VARCHAR(20) COMMENT '日期(周范围)',
    旺旺 VARCHAR(100) COMMENT '旺旺',
    接待人数 INT COMMENT '接待人数',
    平均响应秒 DECIMAL(8,2) COMMENT '平均响应(秒)',
    回复率 TINYINT COMMENT '回复率',
    询单最终付款成功率 TINYINT COMMENT '询单->最终付款成功率',
    上班天数 DECIMAL(4,1) COMMENT '上班天数',
    评价发送率 DECIMAL(6,4) COMMENT '评价发送率',
    客户满意比 TINYINT COMMENT '客户满意比',
    很满意 INT COMMENT '很满意',
    满意 INT COMMENT '满意',
    一般 INT COMMENT '一般',
    不满意 INT COMMENT '不满意',
    很不满意 INT COMMENT '很不满意',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_日期 (日期),
    INDEX idx_旺旺 (旺旺)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪客服数据汇总周数据';
