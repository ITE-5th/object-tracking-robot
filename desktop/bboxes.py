def bboxes_in_position(bboxes, pos):
    result = []
    for bbox in bboxes:
        if is_bbox_in_pos(bbox, pos):
            result.append(bbox[5])

    return result


def is_bbox_in_pos(bbox, pos) -> bool:
    x1, y1, x2, y2 = bbox[:4]
    pos_x, pos_y = pos

    return x1 <= pos_x <= x2 and y1 <= pos_y <= y2

