/**
 * 智能旅行内容库
 *
 * 包含真实景点、餐厅、交通信息
 */

export interface SmartAttraction {
  name: string
  description: string
  highlights: string[]
  suggestedRoute: string
  timeNeeded: string
  tickets: { price: number; notes: string }
  tips: string[]
}

export interface SmartRestaurant {
  name: string
  address: string
  signatureDishes: { name: string; price: number; description: string }[]
  averageCost: number
  tips: string
}

export interface SmartTransport {
  method: string
  duration: string
  cost: number
  tips: string
}

// 智能景点数据库
export const SMART_ATTRACTIONS: Record<string, Record<string, SmartAttraction>> = {
  "杭州": {
    "西湖": {
      name: "西湖",
      description: "西湖是杭州的标志性景点，以其秀丽的湖光山色和丰富的历史文化闻名于世。湖面面积约6.38平方公里，三面环山，一面临城。苏堤春晓、断桥残雪、平湖秋月、花港观鱼等西湖十景各具特色。建议沿苏堤漫步，欣赏湖光山色，感受'人间天堂'的美誉。最佳游览方式是乘坐游船或租借自行车环湖。",
      highlights: [
        "苏堤春晓：长约3公里的苏堤，两旁种满柳树和桃花",
        "断桥残雪：白娘子传说中许仙和白娘子相会之处",
        "三潭印月：西湖最大的岛屿，西湖十景之首"
      ],
      suggestedRoute: "断桥残雪 → 白堤 → 孤山 → 西泠印社 → 苏堤 → 花港观鱼",
      timeNeeded: "3-4小时",
      tickets: { price: 0, notes: "西湖免费开放，游船约55元/人" },
      tips: [
        "穿舒适的步行鞋，全程约5-6公里",
        "春秋季节最佳，注意防晒",
        "避开旅行团高峰期（10-11点，14-15点）"
      ]
    }
  },
  "北京": {
    "故宫": {
      name: "故宫",
      description: "故宫是明清两代皇宫，又称紫禁城，是世界上现存规模最大、保存最完整的木质结构古建筑群。占地72万平方米，建筑面积约15万平方米，有大小宫殿70多座，房屋9000余间。太和殿金銮殿是皇帝举行大典之所，乾清宫是皇帝寝宫，御花园是皇家园林。",
      highlights: [
        "太和殿：故宫最高大的建筑，皇帝登基大典之处",
        "乾清宫：明清皇帝的寝宫和处理政务之地",
        "御花园：皇家花园，堆秀山可俯瞰故宫全景"
      ],
      suggestedRoute: "午门进 → 太和殿 → 中和殿 → 保和殿 → 乾清宫 → 御花园 → 神武门出",
      timeNeeded: "3-4小时",
      tickets: { price: 60, notes: "旺季(4-10月)60元，淡季40元；需网上提前预约" },
      tips: [
        "必须网上预约，现场不售票",
        "从南门(午门)进，北门(神武门)出",
        "参观需要走很多路，穿舒适鞋子"
      ]
    }
  },
  "罗马": {
    "罗马": {
      name: "罗马",
      description: "罗马是意大利的首都，被誉为'永恒之城'。这座拥有近3000年历史的城市汇聚了古罗马时期、文艺复兴时期和巴洛克时期的建筑瑰宝。斗兽场、万神殿、许愿池等世界著名景点遍布全城，每一块石头都诉说着辉煌的历史。建议预留至少3天时间深度游览这座露天博物馆。",
      highlights: [
        "斗兽场：古罗马文明的象征，世界新七大奇迹之一",
        "万神殿：保存最完好的古罗马建筑，穹顶设计令人惊叹",
        "许愿池：罗马最著名的巴洛克式喷泉，据说投币许愿会重返罗马"
      ],
      suggestedRoute: "斗兽场 → 古罗马广场 → 帕拉蒂尼山 → 万神殿 → 许愿池 → 纳沃纳广场",
      timeNeeded: "全天",
      tickets: { price: 16, notes: "斗兽场+古罗马广场+帕拉蒂尼山联票16€，建议提前网上预订免排队" },
      tips: [
        "穿舒适的步行鞋，罗马适合步行探索",
        "注意防盗，特别是在斗兽场和地铁站",
        "大部分餐厅周一至周日12:30-15:00供应午餐，19:30-23:00供应晚餐"
      ]
    }
  },
  "佛罗伦萨": {
    "佛罗伦萨": {
      name: "佛罗伦萨",
      description: "佛罗伦萨是文艺复兴的摇篮，被誉为'艺术之都'。这座托斯卡纳大区的首府城市孕育了达芬奇、米开朗基罗、拉斐尔等艺术巨匠。乌菲兹美术馆收藏了波提切利的《维纳斯的诞生》等旷世杰作，圣母百花大教堂的巨型穹顶是布鲁内莱斯基的建筑奇迹。整座城市本身就是一座露天的文艺复兴艺术博物馆。",
      highlights: [
        "圣母百花大教堂：世界第三大教堂，红色穹顶是佛罗伦萨地标",
        "乌菲兹美术馆：世界最重要绘画博物馆之一",
        "老桥：横跨阿尔诺河的中世纪古桥，珠宝店林立"
      ],
      suggestedRoute: "大教堂广场 → 圣母百花大教堂 → 乔托钟楼 → 老桥 → 乌菲兹美术馆 → 维琪奥桥",
      timeNeeded: "2天",
      tickets: { price: 20, notes: "大教堂穹顶需提前预约，乌菲兹美术馆建议网上订票免排队" },
      tips: [
        "乌菲兹美术馆至少预留3-4小时",
        "佛罗伦萨牛排必须三分熟，五分熟以上会被认为破坏了美食",
        "很多博物馆周一闭馆，提前规划"
      ]
    }
  },
  "威尼斯": {
    "威尼斯": {
      name: "威尼斯",
      description: "威尼斯是建在亚得里亚海泻湖上的水上城市，由118个小岛组成，通过400多座桥梁连接。圣马可广场被誉为'欧洲最美的客厅'，圣马可大教堂融合了拜占庭、哥特和文艺复兴风格。乘坐贡多拉穿梭于蜿蜒的水巷间，欣赏两岸的文艺复兴建筑，是威尼斯独有的浪漫体验。",
      highlights: [
        "圣马可广场：拿破仑誉为'欧洲最美的客厅'",
        "圣马可大教堂：拜占庭建筑杰作，金色马赛克璀璨夺目",
        "总督宫：威尼斯共和国时期的权力中心，走过叹息桥连接监狱"
      ],
      suggestedRoute: "圣马可广场 → 圣马可大教堂 → 总督宫 → 叹息桥 → 雷雅托桥 → 乘坐贡多拉游览",
      timeNeeded: "1-2天",
      tickets: { price: 25, notes: "圣马可大教堂免费但需着装得体，总督宫门票25€" },
      tips: [
        "贡多拉80€/船（白天），100€/船（晚上19:00后），可坐4-5人分摊",
        "使用水上巴士（vaporetto）1日票25€更经济",
        "威尼斯容易迷路，善用Google Maps但也要享受迷路的乐趣"
      ]
    }
  },
  "米兰": {
    "米兰": {
      name: "米兰",
      description: "米兰是意大利的经济和时尚之都，同时也是艺术宝库。米兰大教堂是哥特建筑的巅峰之作，耗时近600年建成，拥有135个尖塔和3400尊雕像。最后的晚餐是达芬奇最著名的壁画之一，收藏于圣玛利亚感恩教堂。蒙特拿破仑街是世界顶级奢侈品购物街。",
      highlights: [
        "米兰大教堂：世界第三大教堂，哥特建筑杰作",
        "最后的晚餐：达芬奇传世名画，需提前数月预约",
        "埃马努埃莱二世拱廊：欧洲最古老的购物中心之一"
      ],
      suggestedRoute: "米兰大教堂 → 大教堂屋顶 → 埃马努埃莱二世拱廊 → 斯卡拉歌剧院 → 圣玛利亚感恩教堂",
      timeNeeded: "1-2天",
      tickets: { price: 20, notes: "大教堂登顶15€，最后的晚餐需提前3个月以上官网预约" },
      tips: [
        "最后的晚餐必须提前很久预约，现场无法购票",
        "教堂着装要求：不穿无袖上衣和短裤/短裙",
        "米兰是购物天堂，但很多商店周日和周一上午关门"
      ]
    }
  },
  "阿玛尔菲": {
    "阿玛尔菲": {
      name: "阿玛尔菲",
      description: "阿玛尔菲是阿玛尔菲海岸最著名的城镇，曾是中世纪强大的海上共和国。这座依山傍海的小镇以壮丽的海岸线、彩色房屋和历史悠久的阿玛尔菲大教堂而闻名。阿玛尔菲海岸被联合国列为世界遗产，是意大利最美丽的海岸线之一。柠檬是当地特产，用于制作著名的柠檬酒Limoncello。",
      highlights: [
        "阿玛尔菲大教堂：阿拉伯-诺曼建筑风格的瑰宝",
        "阿玛尔菲海岸：世界上最美丽的50个地方之一",
        "柠檬步道：徒步穿越柠檬林，欣赏海景"
      ],
      suggestedRoute: "阿玛尔菲镇 → 参观大教堂 → 柠檬步道徒步 → 乘船游览海岸线 → 体验拉韦洛别墅花园",
      timeNeeded: "1天",
      tickets: { price: 10, notes: "大教堂免费， Museo del Duomo 3€" },
      tips: [
        "海岸公路狭窄弯曲，建议自驾选择租车时选择小车型",
        "夏季停车位紧张，建议早到或使用公共交通",
        "品尝当地的柠檬酒Limoncello和海鲜意面"
      ]
    }
  }
}

// 智能餐厅数据库
export const SMART_RESTAURANTS: Record<string, Record<string, SmartRestaurant>> = {
  "杭州": {
    "lunch": {
      name: "楼外楼",
      address: "孤山路30号",
      signatureDishes: [
        { name: "西湖醋鱼", price: 88, description: "杭州名菜，酸甜可口" },
        { name: "东坡肉", price: 68, description: "肥而不腻，入口即化" }
      ],
      averageCost: 120,
      tips: "百年老字号，建议提前预约"
    },
    "dinner": {
      name: "外婆家",
      address: "湖滨银泰in77",
      signatureDishes: [
        { name: "茶香鸡", price: 58, description: "外婆家招牌菜" },
        { name: "青豆泥", price: 22, description: "清香爽口" }
      ],
      averageCost: 80,
      tips: "热门餐厅，建议下午取号"
    }
  },
  "北京": {
    "lunch": {
      name: "全聚德",
      address: "前门大街",
      signatureDishes: [
        { name: "北京烤鸭", price: 198, description: "皮酥肉嫩，配薄饼甜面酱" },
        { name: "鸭汤", price: 38, description: "鲜美滋补" }
      ],
      averageCost: 200,
      tips: "烤鸭需要现烤，建议提前1小时预约"
    },
    "dinner": {
      name: "海底捞",
      address: "王府井店",
      signatureDishes: [
        { name: "麻辣牛肉", price: 58, description: "鲜嫩爽滑" },
        { name: "虾滑", price: 48, description: "Q弹鲜美" }
      ],
      averageCost: 150,
      tips: "服务周到，可提前网上排号"
    }
  },
  "罗马": {
    "lunch": {
      name: "Da Enzo al 29",
      address: "Via dei Vespasiani 29",
      signatureDishes: [
        { name: "Carbonara罗马培根蛋面", price: 14, description: "罗马经典面食，用鸡蛋、培根、佩科里诺干酪制作" },
        { name: "Cacio e Pepe黑胡椒奶酪面", price: 12, description: "简单的面条配佩科里诺干酪和黑胡椒" }
      ],
      averageCost: 35,
      tips: "本地人喜爱的家庭式餐厅，建议提前到达"
    },
    "dinner": {
      name: "Roscioli Salumeria",
      address: "Via dei Giubbonari 21-22",
      signatureDishes: [
        { name: "提拉米苏", price: 8, description: "罗马最好吃的提拉米苏之一" },
        { name: "意式冷切拼盘", price: 25, description: "各种意大利萨拉米和火腿" }
      ],
      averageCost: 60,
      tips: "热门餐厅，建议下午就取号"
    }
  },
  "佛罗伦萨": {
    "lunch": {
      name: "Trattoria Mario",
      address: "Via Rosina 2r",
      signatureDishes: [
        { name: "佛罗伦萨牛排", price: 35, description: "托斯卡纳特产，只煮三分熟" },
        { name: "Ribollita蔬菜汤", price: 10, description: "托斯卡纳传统浓汤" }
      ],
      averageCost: 40,
      tips: "本地人最爱的午餐地点，排队值得等待"
    },
    "dinner": {
      name: "Osteria Santo Spirito",
      address: "Piazza Santo Spirito",
      signatureDishes: [
        { name: "野猪肉意面", price: 16, description: "托斯卡纳山区特色" },
        { name: "佩科里诺干酪梨", price: 12, description: "简单但美味的开胃菜" }
      ],
      averageCost: 45,
      tips: "位于奥尔特拉诺区，氛围轻松友好"
    }
  },
  "威尼斯": {
    "lunch": {
      name: "Trattoria alla Madonna",
      address: "Cannaregio 594",
      signatureDishes: [
        { name: "海鲜 risotto", price: 22, description: "威尼斯经典海鲜烩饭" },
        { name: "沙丁鱼意面", price: 18, description: "威尼斯特色面食" }
      ],
      averageCost: 50,
      tips: "远离圣马可广场，价格更合理"
    },
    "dinner": {
      name: "Osteria alle Testiere",
      address: "Cannaregio 5801",
      signatureDishes: [
        { name: "墨鱼面", price: 20, description: "黑色墨鱼汁制作的威尼斯特色面" },
        { name: "炸海鲜拼盘", price: 25, description: "新鲜炸海鲜" }
      ],
      averageCost: 55,
      tips: "小餐厅只有几桌，必须提前很久预约"
    }
  },
  "米兰": {
    "lunch": {
      name: "Luini Panzerotti",
      address: "Via Santa Radegonda 16",
      signatureDishes: [
        { name: "Panzerotto炸包", price: 3, description: "炸面团包莫扎里拉芝士和番茄" },
        { name: "炸薯角", price: 3, description: "经典米兰街头小吃" }
      ],
      averageCost: 15,
      tips: "米兰最著名的街头小吃，排队很快"
    },
    "dinner": {
      name: "Trattoria del Nuovo Macello",
      address: "Via Cesare Lombroso 20",
      signatureDishes: [
        { name: "米兰式炖小牛胫", price: 24, description: "米兰经典菜肴，藏红花烩饭配小牛胫骨" },
        { name: "烩饭", price: 18, description: "藏红花调味的经典米兰烩饭" }
      ],
      averageCost: 45,
      tips: "远离市中心的本地人餐厅，性价比高"
    }
  },
  "阿玛尔菲": {
    "lunch": {
      name: "Il Pesce",
      address: "Lungomare dei Cavalieri",
      signatureDishes: [
        { name: "海鲜意面", price: 18, description: "当日捕获的新鲜海鲜" },
        { name: "炸海鲜拼盘", price: 25, description: "各种炸海鲜" }
      ],
      averageCost: 40,
      tips: "海边餐厅，美景配美食"
    },
    "dinner": {
      name: "Ristorante Eolo",
      address: "Hotel Belvedere, Via Comunale",
      signatureDishes: [
        { name: "柠檬虾意面", price: 22, description: "阿玛尔菲柠檬制作的当地特色" },
        { name: "Limoncello甜品", price: 8, description: "当地著名柠檬酒" }
      ],
      averageCost: 55,
      tips: "悬崖餐厅，可俯瞰阿玛尔菲海岸全景"
    }
  }
}

// 智能交通数据库
export const SMART_TRANSPORTS: Record<string, SmartTransport> = {
  "杭州": {
    method: "地铁+公交",
    duration: "约40分钟",
    cost: 6,
    tips: "杭州地铁覆盖主要景点，推荐办理杭州通卡"
  },
  "北京": {
    method: "地铁",
    duration: "约50分钟",
    cost: 5,
    tips: "北京地铁便捷，避开早晚高峰(7-9点，17-19点)"
  },
  "罗马": {
    method: "地铁+步行",
    duration: "约30分钟",
    cost: 1.5,
    tips: "罗马地铁仅2条线，很多景点需步行到达，穿舒适的鞋很重要"
  },
  "佛罗伦萨": {
    method: "步行",
    duration: "15-20分钟",
    cost: 0,
    tips: "佛罗伦萨历史中心区很小，几乎所有景点都可以步行到达"
  },
  "威尼斯": {
    method: "水上巴士Vaporetto",
    duration: "约20分钟",
    cost: 7.5,
    tips: "购买24小时或72小时通票更划算，单次票7.5€"
  },
  "米兰": {
    method: "地铁",
    duration: "约30分钟",
    cost: 2,
    tips: "米兰地铁M1/M2/M3线覆盖主要景点，购买一日票7€可在24小时内无限次乘坐"
  },
  "阿玛尔菲": {
    method: "巴士+轮渡",
    duration: "约40分钟",
    cost: 3,
    tips: "海岸公路狭窄弯曲，建议乘坐SITA巴士或轮渡到达其他城镇"
  }
}

/**
 * 获取景点详细信息
 */
export function getAttractionDetails(city: string, location: string): SmartAttraction | null {
  const cityAttractions = SMART_ATTRACTIONS[city]
  if (!cityAttractions) return null
  return cityAttractions[location] || null
}

/**
 * 获取餐厅推荐
 */
export function getRestaurantRecommendation(city: string, mealType: string): SmartRestaurant | null {
  const cityRestaurants = SMART_RESTAURANTS[city]
  if (!cityRestaurants) return null
  return cityRestaurants[mealType] || null
}

/**
 * 获取交通信息
 */
export function getTransportInfo(city: string): SmartTransport | null {
  return SMART_TRANSPORTS[city] || null
}

export default {
  SMART_ATTRACTIONS,
  SMART_RESTAURANTS,
  SMART_TRANSPORTS,
  getAttractionDetails,
  getRestaurantRecommendation,
  getTransportInfo
}
