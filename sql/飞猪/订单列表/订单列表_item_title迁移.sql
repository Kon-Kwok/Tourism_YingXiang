-- =========================================
-- 飞猪订单列表：新增商品标题字段
-- 目的：保存补差订单等没有“套餐类型”SKU 的原始商品标题
-- 目标表：feizhu.fliggy_order_list
-- 字段来源：订单接口 itemInfo.itemTitle
-- =========================================
USE feizhu;

SET @item_title_column_exists := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'feizhu'
      AND TABLE_NAME = 'fliggy_order_list'
      AND COLUMN_NAME = 'item_title'
);

SET @add_item_title_sql := IF(
    @item_title_column_exists = 0,
    'ALTER TABLE fliggy_order_list ADD COLUMN item_title VARCHAR(300) NULL COMMENT ''商品标题'' AFTER order_id',
    'SELECT ''item_title column already exists'' AS message'
);

PREPARE add_item_title_stmt FROM @add_item_title_sql;
EXECUTE add_item_title_stmt;
DEALLOCATE PREPARE add_item_title_stmt;
