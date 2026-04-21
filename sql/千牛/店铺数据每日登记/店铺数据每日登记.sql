-- =========================================
-- 店铺数据每日登记
-- 文件: 店铺数据每日登记.xlsx
-- =========================================
USE qianniu;

CREATE TABLE IF NOT EXISTS qianniu_shop_data_daily_registration (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    日期 DATE NOT NULL COMMENT '日期',
    PV BIGINT COMMENT 'PV',
    UV BIGINT COMMENT 'UV',
    PaidUV INT COMMENT 'PaidUV',
    关注店铺人数 INT COMMENT '关注店铺人数',
    GMV DECIMAL(14,2) COMMENT 'GMV',
    咨询人数 INT COMMENT '咨询人数',
    咨询转化率 DECIMAL(10,6) COMMENT '咨询转化率',
    下单买家数 INT COMMENT '下单买家数',
    下单转化率 DECIMAL(10,6) COMMENT '下单转化率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_日期 (日期)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='千牛店铺数据每日登记';
