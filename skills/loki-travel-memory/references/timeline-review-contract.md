# 时间线与验收契约

这份契约用于把“看起来差不多”变成可追踪的制作约束。每次渲染前记录所有权与时间，渲染后仍需查看实际画面和连续播放；JSON 检查不能代替审美或听审。

## 时间线对象必须有所有权

| 对象 | 必需字段 | 说明 |
|---|---|---|
| scene | `id/start/end/event_id/media_ids/primary_subject/protected_regions/max_emphasis_overlays/layout_grammar/layout_reason` | 画面场景、核心表达、不可遮挡区、文字预算与版式选择 |
| transition | `id/start/end/from_scene_id/to_scene_id/kind/match_basis/reason/audio_bridge/focus_owner_before/focus_owner_after/moving_focus_layers/handoff_mode/music_cue` | 相邻场景的连接、焦点交接与真实音乐提示点；直切也要记录 |
| subtitle | `id/start/end/text/source_id` | 同期声字幕；来源可追溯 |
| overlay | `id/start/end/role/owner_scene_id/exit_mode` | 花字、小动效或事件包装 |
| music | `id/start/end/source/title/artist/source_in/source_out/owner_scene_ids/entry_mode/entry_reason` | 歌曲实际取用区间、所属画面与进入理由 |
| speech | `id/start/end/source_id` | 同期声实际入出点 |

可直接复制 [timeline-review-contract.example.json](timeline-review-contract.example.json) 作为起点，再执行自动检查。

`role` 至少区分 `chapter_subtitle`、`location_badge`、`speech_subtitle`、`flower_copy`。同一套造型不能覆盖全部角色。

`exit_mode`：

- `with_owner`：花字和所属画面进入同一退出转场；`overlay.end` 与 `scene.end` 误差最多一帧。
- `with_subtitle`：花字解释一句同期声；必须设置 `linked_subtitle_id`，两者结束时间误差最多一帧。
- `explicit`：有内容理由的独立退出；必须写 `exit_reason`，不能仅写“好看”。

绑定的是所有权，不是视觉位置。花字可以放在负空间，但不能因为放在底板上就脱离所属照片或声音。

`primary_subject` 写观众这一拍必须看到什么；`protected_regions` 写不得被小图、文字或贴纸遮挡的区域，可以为空数组，但核心主体画面不应为空。`max_emphasis_overlays` 是该 scene 最多允许的强调层数量，只统计 `flower_copy`、`progress_number` 和 `explanatory_copy`，不把同期声字幕与必要导航混在一起计算。

`layout_grammar` 写本拍的编排逻辑，例如 `fullscreen_exposure`、`hero_detail_relay`、`scenery_then_people`、`food_hero_detail`、`single_fullscreen` 或本项目新语法；`layout_reason` 必须说明为何适合这些素材，不能只写“沿用模板”。

## 转场必须先写镜头关系

每两个相邻 scene 都要有一条 transition 记录，包括直接切。`kind` 写实际实现，例如 `direct_cut`、`sound_bridge`、`match_cut`、`occlusion` 或 `graphic_morph`；`match_basis` 写动作、方向、形状、光色、尺度、主体、声音或意义对照等真实依据，不能只写“高级”“更帅”。`reason` 说明它怎样服务内容，`audio_bridge` 明确 `none`、`j_cut`、`l_cut` 或具体声音来源。

`focus_owner_before` 与 `focus_owner_after` 记录交接前后第一视线属于哪张图或哪段视频。`moving_focus_layers` 只列真正发生接管、位移、放大或缩小的焦点层，默认最多一个；非焦点层可以保持或淡出。`handoff_mode` 写 `detail_to_hero`、`fullscreen_dissolve`、`scenery_to_people`、`direct_cut` 或本项目定义的真实交接。若确需多个焦点层同时运动，必须设置 `allow_multi_focus=true` 并写可检查的 `multi_focus_reason`。`music_cue` 写本剪口使用的真实依据，例如 `strong_beat@7.152`、`phrase_end@13.540`、`spoken_word_complete` 或 `none`，不能只写“卡点”。

英雄转场至少要有两层可验证依据，并在制作前确认源素材真的提供所需运动、遮挡或构图。没有依据时按“声音桥＋直切 → 简洁叠化 → 直接切”降级，不能靠冰雾、蒸汽、闪白或旋转遮住无关场景。自动检查只确认记录、引用和接缝覆盖；渲染后仍要连续观看转场前后至少 3 秒，判断它是否突兀、误导空间关系或抢过内容。

## 同步退出的渲染规则

1. 画面转场开始时，`with_owner` 花字必须存在于 outgoing 合成层中，与画面一起淡出/切走；不能先从干净底图消失，再单独转照片。
2. `with_subtitle` 花字在字幕出现后进入可以有设计延迟，但结束帧必须一致。24 fps 项目允许的最大误差为 `1/24s`。
3. 字幕/花字结束后的第一帧不得残留描边、底板、气泡或装饰线。下一镜不得继承上一镜的花字。
4. 同一句花字跨多张同事件照片时，把它绑定到该照片组 scene；若只解释其中一张，随该张切走，不跨组悬空。
5. 章节标题、角标等持续导航不是花字；它们可按章节规则持续，但地点变化时必须更新。

## 渲染后抽帧与连续观看

对每个关键退出点提取：

- 退出前一帧：`end - 1/fps`
- 退出帧：`end`
- 退出后一帧：`end + 1/fps`
- 转场较长时，再抽取转场 25%、50%、75% 三帧。

检查花字和画面是否共同衰减、字幕/花字是否同帧消失、是否有闪白/残影、下一镜是否串字。抽帧用于精确定位；仍要连续播放该点前后至少 3 秒，确认体感顺畅。

对焦点接力还要检查 25%/50%/75% 三帧：是否始终只有一个明确焦点在接管，非焦点图片有没有交叉穿越或突然换位，任何中间态有没有遮住 `protected_regions`。首尾好看、中间混乱仍判定为失败。

## 重复照片与候选门槛

- 时间线中同一 `source_id` 重复出现时默认报错；确需复现必须写 `allow_repeat=true` 和叙事理由。
- 高辨识度主体还要做视觉重复检查，不能只查文件 ID。倒木、特殊姿势、独特自拍、地标全景和同角度连拍尤其容易被用户记住。
- 用户要求先看替换方案时，候选必须来自未使用素材，并放入真实版式；不能只给缩略图，也不能先改完再让用户追认。

## 版式与文字检查

- 空白必须承担标题、呼吸或视线引导；如果只是原照片无信息区域，优先合理裁切。为了塞文字硬缩照片产生的无意义留白不合格。
- 主体需要完整时不强裁；食物、人物和关键风景先看清，再谈信息量。
- 先核对每个 scene 的 `primary_subject` 与 `protected_regions`。重要大景先完整展示，人物、自拍或细节另起一拍；不能把自拍条压在湖面、山脊或瀑布等核心区域。
- 章节标题和 DAY/日期即使位置正确，也必须与底板拉开明度或色相；不能因颜色相近被纹理吞掉。
- 花字、字幕、地点角标应分别使用不同承载逻辑，例如开放式描边/插画、稳定字幕底、导航角标；不得全做成同色圆角胶囊。
- 每个 scene 的强调层不得超过 `max_emphasis_overlays`。解释性小字若只复述照片可见内容，直接删除；01/02/03/04 只有承担真实进度时才标为 `progress_number`。

## 声音检查

- 两段同期声不得重叠；连续说话之间不要插入几秒独立 BGM 与图片。
- 短引导原声可保留低位 BGM；音乐压低和恢复要有包络，不能骤停骤起。
- 换歌在乐句、内容桥梁和画面转换三者之间寻找落点。`source_in/source_out` 必须是实际音源区间，`owner_scene_ids` 必须对应这首歌服务的内容。`entry_mode=with_owner` 时不得早于第一所属画面进入；确有内容桥时用 `entry_mode=bridge` 并写明 `entry_reason`。两首歌交叠必须双方设置 `allow_overlap=true` 并记录 `overlap_reason`，不能把三秒提前进入当成默认交叉淡化。
- 检查完整混音，也导出独立音乐分轨，避免把人声起音误判成换歌断裂。节拍/波形检测只提供候选点，最终剪口仍需实际听审或明确标记未听。
- 片尾单独设计音乐收束，避免最后一句话后音乐突然回弹再骤停。
- 实际人工听审、音频模型、ASR、响度/波形与解码检查分别记录；后四项不能替代人工听审。

## 自动检查

项目将上述字段保存为 JSON 后运行：

```bash
python3 scripts/audit_timeline_contract.py review-contract.json
```

脚本检查场景边界、内容保护字段、强调文字预算、每组相邻场景的转场记录与接缝、单焦点运动、花字所有权、`with_owner`/`with_subtitle` 结束帧、音乐所属画面与交叠理由、同期声重叠、字幕重叠和同一媒体重复使用。它通过后仍要完成渲染后抽帧、连续播放和声音听审。
