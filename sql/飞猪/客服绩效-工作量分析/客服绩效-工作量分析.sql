-- =========================================
-- 客服绩效-工作量分析
-- 文件: 客服绩效-工作量分析.xlsx
-- =========================================
USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS fliggy_customer_service_performance_workload_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    旺旺昵称 VARCHAR(100) COMMENT '旺旺昵称',
    咨询人数 INT COMMENT '咨询人数',
    接待人数 INT COMMENT '接待人数',
    直接接待人数 INT COMMENT '直接接待人数',
    转入人数 INT COMMENT '转入人数',
    转出人数 INT COMMENT '转出人数',
    总消息 INT COMMENT '总消息',
    买家消息 INT COMMENT '买家消息',
    客服消息 INT COMMENT '客服消息',
    答问比 DECIMAL(6,4) COMMENT '答问比',
    客服字数 INT COMMENT '客服字数',
    最大同时接待 DECIMAL(6,1) COMMENT '最大同时接待',
    未回复人数 INT COMMENT '未回复人数',
    旺旺回复率 DECIMAL(4,3) COMMENT '旺旺回复率',
    慢响应人数 INT COMMENT '慢响应人数',
    长接待人数 INT COMMENT '长接待人数',
    首次响应秒 DECIMAL(8,2) COMMENT '首次响应(秒)',
    平均响应秒 DECIMAL(8,2) COMMENT '平均响应(秒)',
    平均接待秒 VARCHAR(20) COMMENT '平均接待(秒)',
    平均接待时长秒 DECIMAL(8,2) COMMENT '平均接待时长(秒)',
    date_time DATE COMMENT 'Date',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_旺旺昵称 (旺旺昵称),
    INDEX idx_date_time (date_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪客服绩效工作量分析';
