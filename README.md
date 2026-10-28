# 旅行回忆 Vlog Skill

**把照片和短视频交给 AI，从筛选到成片，少一点翻相册式剪辑。**

由赛博小熊猫 Loki 整理。方法说明与样片页：https://loki-os.hiloki.ai/methods/travel-memory/ 。来自真实旅行剪辑中反复修改形成的方法，现提供脱敏公开版。适合照片占多数的独行、朋友同行、家庭旅行，也能按请求为同行者单独剪一条。

方法说明与样片见场刊页：[旅行回忆工作流](https://loki-os.hiloki.ai/methods/travel-memory/)。

## 它会怎么做

| 阶段 | 具体工作 |
| --- | --- |
| 素材筛选 | 按实际拍摄时间整理；同景连拍选优；区分主图、细节、备用，不删除原片 |
| 行程与故事 | 恢复事件顺序，只集中问影响故事的未知项，不要求重新口述完整行程 |
| 原创设计 | 根据目的地、照片和旅行目的定方向；先景后人、主图与细节接力，保护脸和景观 |
| 动态与节奏 | 每次交接一个焦点，结合真实音乐强弱，不靠多图乱飞或快闪堆数量 |
| 声音与文字 | 保留完整同期声、音乐适度压低；字幕、花字、角标分层，绑定画面或声音同步退出 |
| 调色与验收 | 按每张原片调整；检查裁切、重复、转场和声音，交付可追溯工程 |

这是一套给 AI 执行的工作流，**不是独立剪辑软件，也不自带一键渲染器**。安装后能做到什么，取决于 AI 宿主是否具备文件访问、图像查看、视频处理、转写和渲染能力。审计脚本只检查时间线约束，不能判断审美，也不能代替实际听审。

## 这次升级解决什么

v1.1.0 把反复返工的意见整理成具体执行流程：

- **新素材从哪里开始**：真实能力试跑 → 全量覆盖 → 事件与精选 → 设计 → 难点连续样片 → 整片。
- **改旧片怎样才算提升**：区分内容、关系、节奏和表现问题，保留认可基线，用同事件前后片段证明改动。
- **人需要参与哪里**：AI 承担筛选和制作，人补充素材看不出的背景、少量关键选择和最终口味判断；不会听音的环境需明确听审安排。
- **不把个人模板当标准**：歌曲、IP、隐私和具体版式属于本次项目；通用的是内容保护、事实、声音完整和同步退出。

看 [完整制作流程](skills/loki-travel-memory/references/production-workflow.md)、[反馈如何变成规则](skills/loki-travel-memory/references/feedback-to-decisions.md)、[城市逛吃示例](skills/loki-travel-memory/references/city-food-worked-example.md) 和 [旧片升级方法](skills/loki-travel-memory/references/revision-and-proof.md)。

**验证边界**：本次完成文档/引用检查与 14 项时间线脚本回归测试，没有完成另一趟全新旅行的端到端影片验证。规则能减少基础错误，不能保证不同模型的审美达到同一水平。欢迎用真实、脱敏案例反馈，包括“改了看不出提升”。

## 下载与安装

[下载 v1.1.0 Skill 压缩包](https://github.com/loki2046-mao/loki-travel-memory/releases/download/v1.1.0/loki-travel-memory-v1.1.0.zip) · [浏览 Skill](skills/loki-travel-memory/SKILL.md) · [所有版本](https://github.com/loki2046-mao/loki-travel-memory/releases)

下载后解压，将完整的 `loki-travel-memory` 文件夹交给支持 Skill 的 AI 工具安装，保留 `references`、`scripts` 和 `agents` 子目录。

Codex 本地安装：将该文件夹放进 `~/.codex/skills/`。如果已有同名个人版本，先备份或让 AI 比较差异，不要直接覆盖。重新打开会话后，可明确调用 `$loki-travel-memory`。

也可以克隆仓库后，将 `skills/loki-travel-memory` 文件夹安装到相应位置：

```sh
git clone https://github.com/loki2046-mao/loki-travel-memory.git
```

其他工具的 Skill 目录以其支持方式为准；未对所有宿主逐一测试。没有媒体处理工具的纯聊天环境，可以用于规划和审片建议，不能承诺直接输出视频。

## 直接这样开始

```text
使用 $loki-travel-memory 处理我提供的旅行素材文件夹。
先按实际拍摄时间通看素材，整理行程和候选照片，拿不准的地方集中问我。
照片为主，保留原文件；先做一段带真实音乐和同期声的连续样片，
我看过后再扩展整片。片子统一横屏。
这趟旅行我最想记住的是……；希望使用的音乐或参考是……。
```

最后两项可留空，让 AI 从素材中提出建议。横竖画幅、长短、人物版本按你的实际用途调整。第一次先做短样片，能更早发现选图、排版或音乐不合口味。

## 如果是改已有片

```text
使用 $loki-travel-memory 改进这条已有 vlog，原片和工程在我提供的目录里。
先看旧片并诊断最影响观感的问题，保留我认可的设计。
选一个问题明显的事件，做带真实声音的前后对照；
确认改动确实更清楚、更顺之后，再应用到整片。
```

不需要先写完整行程或填写长问卷。素材看不出的地点/背景再集中补充；歌曲可指定，也可让 AI 提少量候选。没有原工程时先说明能做的修改范围。

## 包含什么

- `SKILL.md`：执行入口和制作顺序。
- `references/`：选片、行程恢复、原创设计、照片编排、声音、调色与验收方法。
- `references/user-profile.md`：每次根据使用者填写的偏好，不继承作者私人习惯。
- `references/timeline-review-contract.example.json`：虚构示例，不含真实旅行媒体。
- `scripts/audit_timeline_contract.py`：Python 3.9+、仅使用标准库的静态审计脚本。

在 Skill 文件夹内运行示例：

```sh
python3 scripts/audit_timeline_contract.py references/timeline-review-contract.example.json
```

脚本检查相邻场景转场记录、焦点数量、花字所属画面/字幕的退出时间、重复媒体、对白重叠、音乐所属场景与交叠理由。它不解码视频、不自动识别人脸遮挡、不判断字词正确性，也不验证音乐是否听起来顺。

## 隐私与素材

公开包仅包含方法文档、工具脚本和虚构数据。不含作者的照片、录像、声音、IP 图片、真实行程索引、家庭称呼、聊天原文、账号凭证或商业歌曲。历史参考研究只保留公开出处与观察范围，不分发参考片。

制作时原素材保持只读，输出写入独立项目。素材交给云服务处理前，确认该工具的数据处理方式符合你的需求。Skill 不授予任何歌曲、肖像或第三方素材的使用权。

## 反馈与许可

欢迎在 [Issues](https://github.com/loki2046-mao/loki-travel-memory/issues) 提交问题，说明素材类型、希望达到的效果和实际问题。请使用已脱敏的例子，不上传私人媒体、GPS 或完整运行日志。

本仓库自行编写的文档与代码按 [MIT License](LICENSE) 提供。第三方参考作品不属于本许可范围。
