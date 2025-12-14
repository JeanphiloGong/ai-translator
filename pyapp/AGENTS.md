# **AGENTS.md（后端开发规范版）**

### Backend Code Authoring Principles for AI Agents

> 基于 **Robert C. Martin（Bob 大叔）Clean Architecture**、**Martin Fowler** 的企业级后端实践、以及 **DDD 领域驱动设计流派** 的综合理念。

---

# **📘 概述**

本文件用于指导 AI Agents 在本项目中**如何编写高质量的后端代码**。
这些规则来自多位后端架构领域的大师，包括：

* **Robert C. Martin（Uncle Bob）** → Clean Architecture
* **Martin Fowler** → Patterns of Enterprise Application Architecture
* **Eric Evans** → Domain-Driven Design
* **Sam Newman** → Microservices Patterns

AI 在编写后端代码时必须遵循这些大师级理念，以确保系统可维护、可扩展、可演化。

---

# **🎯 AI 编写后端代码的核心目标**

1. **可读性优先（Readable First）**
2. **逻辑清晰（Explicit Logic）**
3. **松耦合（Loose Coupling）**
4. **强边界（Clear Boundaries）**
5. **面向接口（Dependency Inversion）**
6. **可测试（Testable Architecture）**

---

# **🏛 后端架构大师：理念来源说明**

## **1. Clean Architecture（Robert C. Martin）**

AI 必须遵循：

* 不允许业务逻辑依赖基础设施
* 依赖方向必须指向稳定的领域层
* Controller/Handler 不得包含业务逻辑
* 数据库为细节，绝不能侵入领域模型
* 所有核心逻辑应该纯净、无副作用

**简化的依赖图：**

```
Entities（Domain）
↑
Use Cases（Service/Logic）
↑
Interface Adapters（Controller/DTOs）
↑
Frameworks & Drivers（DB / HTTP / MQ）
```

---

## **2. Martin Fowler 的企业级模式**

AI 在写后端代码时必须遵循：

* **Repository Pattern**（持久化与业务分离）
* **Service Layer Pattern**（业务集中，不散落 handler）
* **DTO Pattern**（输入输出必须显式模型）
* **Circuit Breaker / Retry Pattern**（服务间调用需考虑稳定性）

---

## **3. DDD（Eric Evans）**

AI 应坚持：

* 模型优先（Model-First Development）
* 聚合（Aggregate）必须维护业务不变量
* 值对象（Value Object）必须不可变
* 应用服务（Application Service）只协调，不做业务
* 领域服务（Domain Service）只负责业务规则
* 命令与查询必须分离（CQRS）

---

# **🧠 AI 写后端代码时必须遵守的十大黄金法则**

## **📌 法则 1：业务逻辑必须在 Service，不在 Controller**

Controller 只做：

* 参数校验
* 调用 service
* 返回结果

Service 才是业务核心。

---

## **📌 法则 2：模型必须明确分层**

AI 编写后端代码时必须区分：

* **DTO（输入输出）**
* **Entity（领域模型）**
* **Repository Object（持久化模型）**

禁止混为一体。

---

## **📌 法则 3：所有外部依赖必须接口化（依赖倒置）**

AI 写的后端代码中：

* 调用 DB → 通过 Repository 接口
* 调用第三方 API → 通过 Provider 接口
* 调 MQ / Cache → 通过 Gateway 层
* 禁止业务层直接依赖外部库

这是 **Uncle Bob 的 DIP 原则**。

---

## **📌 法则 4：函数必须保持短小、纯净、单一职责**

AI 必须保证：

* 一个函数只做一件事
* 无隐式副作用
* 逻辑可读，不嵌套多层条件

---

## **📌 法则 5：业务流程必须显式（No Magic）**

AI 必须将流程写得清晰可读：

✔ 显式声明步骤
✔ 显式声明异常条件
✔ 显式返回错误原因
❌ 不允许“魔法行为”或自动推断流程

---

## **📌 法则 6：错误必须被分类与显式处理**

错误必须分：

* 用户可预期错误（业务错误）
* 系统错误（不可预期）
* 外部依赖错误（API / DB 失败）

AI 写代码时必须提供：

* 清晰的错误模型
* 不吞错误
* 不隐藏异常

---

## **📌 法则 7：任何数据流动必须具备幂等性与可恢复性**

尤其适用于：

* HTTP 再试
* MQ 消费
* 分布式任务

这是 **后端工程的韧性要求**。

---

## **📌 法则 8：所有代码必须可测试（Testable by Design）**

AI 写代码时应该：

* 避免静态绑定
* 借助接口注入依赖
* 避免隐藏逻辑
* 避免“God Object”

---

## **📌 法则 9：不允许跨层泄漏（Layer Leakage）**

AI 编写代码时禁止：

* Controller 使用 ORM Model
* Repository 返回业务对象未封装
* 领域层访问基础设施

---

## **📌 法则 10：代码即是工程文化（Readable > Clever）**

AI 必须遵循：

* 优雅清晰胜过聪明奇技
* 写给人类看，而不是写给机器看
* 任何一段业务逻辑必须可被同事在 1 分钟内理解

---

# **🧩 AI 生成后端代码的结构规范**

当 AI 生成后端代码时，可以参考如下结构：（示例）

```
/internal
  /domain
    /user
      entity.go
      value_object.go
      service.go
  /app
    user_service.go
  /infra
    db
      user_repository.go
    external
      sms_provider.go
  /interfaces
    http
      user_handler.go
    dto
      user_request.go
      user_response.go
```

AI 必须自动识别并保持分层一致性。

---

# **🎓 该方法为谁在用？（大师出处）**

本规范综合了四位后端架构大师的方法：

| 大师                              | 理念                 | 在本规范中的体现                     |
| ------------------------------- | ------------------ | ---------------------------- |
| **Uncle Bob（Robert C. Martin）** | Clean Architecture | 分层边界、依赖倒置、内核纯净               |
| **Martin Fowler**               | 企业级架构模式            | DTO、Repository、Service Layer |
| **Eric Evans**                  | DDD                | 聚合、实体、领域服务、值对象               |
| **Sam Newman**                  | 微服务模式              | 隔离、弹性、可扩展、边界清晰               |

你可以在 AGENTS.md 中写明：

> 本项目的后端代码生成规范建立在 **Uncle Bob、Martin Fowler、Eric Evans、Sam Newman** 的经典方法之上，要求 AI Agents 在任何后端代码生成任务中严格遵循这些大师级理念。

---

# **🔚 总结声明（AI 必须遵守）**

当 AI 为后端生成代码时：

* 必须遵循 **Clean Architecture**
* 必须遵循 **DDD 原则**
* 必须使用 **Pattern-Based Architecture**
* 必须提供可读、可维护、可测试的代码
* 不允许编写“低质量、脚本式后端”

AI 写后端代码必须像 **Fowler + Bob + DDD 高手的结合体**。


