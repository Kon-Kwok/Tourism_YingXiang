-- =========================================
-- 客服数据汇总-日数据
-- 文件: 客服数据汇总-日数据.xlsx
-- =========================================
USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS fliggy_customer_service_data_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    日期 DATE NOT NULL COMMENT '日期',
    旺旺 VARCHAR(100) COMMENT '旺旺',
    接待人数 INT COMMENT '接待人数',
    平均响应秒 DECIMAL(8,2) COMMENT '平均响应(秒)',
    回复率 DECIMAL(4,3) COMMENT '回复率',
    询单最终付款成功率 DECIMAL(6,4) COMMENT '询单->最终付款成功率',
    上班天数 DECIMAL(4,1) COMMENT '上班天数',
    评价发送率 DECIMAL(6,4) COMMENT '评价发送率',
    客户满意比 VARCHAR(10) COMMENT '客户满意比',
    很满意 VARCHAR(10) COMMENT '很满意',
    满意 VARCHAR(10) COMMENT '满意',
    一般 VARCHAR(10) COMMENT '一般',
    不满意 VARCHAR(10) COMMENT '不满意',
    很不满意 VARCHAR(10) COMMENT '很不满意',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_日期 (日期),
    INDEX idx_旺旺 (旺旺)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪客服数据汇总日数据';
