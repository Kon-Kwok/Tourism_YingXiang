-- =========================================
-- 飞猪店铺日度关键数据
-- 文件: 飞猪店铺日度关键数据.xlsx
-- =========================================
USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS qianniu_fliggy_shop_daily_key_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    日期 DATE NOT NULL COMMENT '日期',
    total_pv BIGINT COMMENT 'Total PV (总浏览数)',
    total_uv BIGINT COMMENT 'Total UV(总访客数)',
    流量来源广告_uv BIGINT COMMENT '流量来源广告UV',
    流量来源平台_uv BIGINT COMMENT '流量来源平台UV',
    流量来源汇总 BIGINT COMMENT '流量来源汇总',
    直引万品点击量 BIGINT COMMENT '直引万品点击量',
    chat_volume BIGINT COMMENT 'Chat Volume(询单量)',
    total_bookings BIGINT COMMENT 'Total Bookings(总售卖件数)',
    total_pax DECIMAL(10,2) COMMENT 'Total PAX(总售卖乘客数)',
    gmv DECIMAL(14,2) COMMENT 'GMV',
    pingxiaobao_cost DECIMAL(14,2) COMMENT '品销宝费用',
    pingxiaobao_imp BIGINT COMMENT '品销宝展示',
    pingxiaobao_click BIGINT COMMENT '品销宝点击',
    tmall_express_cost DECIMAL(14,2) COMMENT '直通车费用',
    tmall_express_imp BIGINT COMMENT '直通车展示',
    tmall_express_click BIGINT COMMENT '直通车点击',
    gravity_rubiks_cube_cost DECIMAL(14,2) COMMENT '引力魔方费用',
    gravity_rubiks_cube_imp BIGINT COMMENT '引力魔方展示',
    gravity_rubiks_cube_click BIGINT COMMENT '引力魔方点击',
    mansa_dae_cost DECIMAL(14,2) COMMENT '万相台费用',
    mansa_dae_views BIGINT COMMENT '万相台观看量',
    mansa_dae_click BIGINT COMMENT '万相台点击',
    super_recommendation_cost DECIMAL(14,2) COMMENT '超推Cost',
    cost_total DECIMAL(14,2) COMMENT 'Cost Total',
    imp_total BIGINT COMMENT 'IMP Total',
    click_total BIGINT COMMENT 'Click Total',
    pingxiaobao_booked_cabin DECIMAL(10,2) COMMENT '品销宝Booked Cabin',
    tmall_express_booked_cabin BIGINT COMMENT '直通车Booked Cabin',
    gravity_rubiks_cube_booked_cabin DECIMAL(10,2) COMMENT '引力魔方Booked Cabin',
    mansa_dae_booked_cabin DECIMAL(10,2) COMMENT '万相台Booked Cabin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_日期 (日期)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='千牛飞猪店铺日度关键数据';
