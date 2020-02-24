
### ai-service 注册 [ ai client -> server ]
{"cmd": "register", "type": "aaa"}

### pc 发送细胞类型分析的请求 [ client -> server ]
{"cmd": "analysis", "type": "aaa", "image": "base64....."}

### ai-service 回应 细胞类型分析的结果 [ ai client -> server ]
{"cmd": "analysis_result", "type": "aaa", "channel": "200224074536104298", "object_type": "xxx"}
