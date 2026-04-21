CREATE TABLE IF NOT EXISTS sycm_collection_batches (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '批次ID',
    page_code VARCHAR(64) NOT NULL COMMENT '页面编码',
    biz_date DATE NOT NULL COMMENT '业务日期',
    shop_name VARCHAR(255) NOT NULL COMMENT '店铺名称',
    status VARCHAR(32) NOT NULL COMMENT '批次状态',
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    finished_at TIMESTAMP NULL DEFAULT NULL COMMENT '结束时间',
    error_message TEXT NULL COMMENT '错误信息'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生意参谋采集批次';

CREATE TABLE IF NOT EXISTS sycm_api_raw_payloads (
    batch_id BIGINT NOT NULL COMMENT '批次ID',
    endpoint_code VARCHAR(64) NOT NULL COMMENT '接口编码',
    payload_json LONGTEXT NOT NULL COMMENT '原始JSON响应',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (batch_id, endpoint_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生意参谋原始接口响应';

CREATE TABLE IF NOT EXISTS sycm_homepage_metrics (
    biz_date DATE NOT NULL COMMENT '业务日期',
    page_code VARCHAR(64) NOT NULL COMMENT '页面编码',
    shop_name VARCHAR(255) NOT NULL COMMENT '店铺名称',
    metric_code VARCHAR(128) NOT NULL COMMENT '指标编码',
    metric_value DECIMAL(20,6) NULL COMMENT '指标值',
    cycle_crc DECIMAL(20,10) NULL COMMENT '环比',
    sync_crc DECIMAL(20,10) NULL COMMENT '同比/对比',
    year_sync_crc DECIMAL(20,10) NULL COMMENT '去年同期',
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
    batch_id BIGINT NOT NULL COMMENT '批次ID',
    PRIMARY KEY (biz_date, page_code, metric_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生意参谋首页核心指标';

CREATE TABLE IF NOT EXISTS sycm_homepage_trends (
    biz_date DATE NOT NULL COMMENT '业务日期',
    stat_date DATE NOT NULL COMMENT '统计日期',
    page_code VARCHAR(64) NOT NULL COMMENT '页面编码',
    shop_name VARCHAR(255) NOT NULL COMMENT '店铺名称',
    metric_code VARCHAR(128) NOT NULL COMMENT '指标编码',
    self_value DECIMAL(20,6) NULL COMMENT '本店值',
    rival_avg_value DECIMAL(20,6) NULL COMMENT '同行同层均值',
    rival_good_value DECIMAL(20,6) NULL COMMENT '同行优秀值',
    collected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
    batch_id BIGINT NOT NULL COMMENT '批次ID',
    PRIMARY KEY (biz_date, stat_date, page_code, metric_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生意参谋首页趋势序列';
