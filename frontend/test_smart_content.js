/**
 * 测试智能旅行内容库
 */

// 模拟景点数据
const SMART_ATTRACTIONS = {
  "罗马": {
    "罗马": {
      name: "罗马",
      description: "罗马是意大利的首都，被誉为'永恒之城'...",
      highlights: ["斗兽场：古罗马文明的象征"],
      suggestedRoute: "斗兽场 → 古罗马广场 → 万神殿",
      timeNeeded: "全天",
      tickets: { price: 16, notes: "建议提前网上预订" },
      tips: ["穿舒适的步行鞋", "注意防盗"]
    }
  }
};

const SMART_RESTAURANTS = {
  "罗马": {
    "lunch": {
      name: "Da Enzo al 29",
      address: "Via dei Vespasiani 29",
      signatureDishes: [
        { name: "Carbonara罗马培根蛋面", price: 14, description: "罗马经典面食" }
      ],
      averageCost: 35,
      tips: "建议提前到达"
    }
  }
};

// 测试函数
function test() {
  console.log('=== 智能内容库测试 ===');

  // 测试景点
  const city = '罗马';
  const location = '罗马';

  const cityAttractions = SMART_ATTRACTIONS[city];
  const attraction = cityAttractions?.[location];

  if (attraction) {
    console.log('✅ 景点测试成功');
    console.log(`   名称: ${attraction.name}`);
    console.log(`   描述: ${attraction.description.substring(0, 50)}...`);
    console.log(`   亮点: ${attraction.highlights[0]}`);
    console.log(`   门票: €${attraction.tickets.price}`);
  } else {
    console.log('❌ 景点测试失败');
  }

  // 测试餐厅
  const mealType = 'lunch';
  const cityRestaurants = SMART_RESTAURANTS[city];
  const restaurant = cityRestaurants?.[mealType];

  if (restaurant) {
    console.log('✅ 餐厅测试成功');
    console.log(`   名称: ${restaurant.name}`);
    console.log(`   招牌菜: ${restaurant.signatureDishes[0].name} - €${restaurant.signatureDishes[0].price}`);
  } else {
    console.log('❌ 餐厅测试失败');
  }

  console.log('\n测试数据示例:');
  console.log(JSON.stringify(attraction, null, 2));
}

test();
