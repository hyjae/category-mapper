-- Delete based on update_time
-- Records in cat_map with the same cat_id will be removed(ON DELETE SET CASCADE)
-- Records in ep_info table with the same cat_id  (ON DELETE SET NULL);

SET SQL_SAFE_UPDATES = 0;

DELETE FROM ITEM_CAT
WHERE CAT_ID IN (
  SELECT CAT_ID
  FROM CAT_MAP
  WHERE UPDATE_TIME > 20191010
);

SET SQL_SAFE_UPDATES = 1;

ALTER TABLE ITEM_CAT AUTO_INCREMENT = 10582;
