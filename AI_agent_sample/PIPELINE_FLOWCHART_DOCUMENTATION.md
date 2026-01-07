# AI-Powered Social Media Content Pipeline

> **System Status Note:**
> This documentation describes the complete architecture of a self-improving AI content pipeline. The system is **production-capable** and was developed as a comprehensive case study in end-to-end AI automation.
>
> **Note on Social Media Integration:** While the publishing pipeline is fully functional and tested, the author does not maintain active social media accounts. Social media publishing was selected as an ideal use case because it demonstrates the full complexity of AI-powered content workflows: generation, multi-stage quality assessment, scheduling, and feedback loops. The architecture is production-ready but operates primarily as a demonstration of these capabilities.
>
> **Fully Operational:**
> - End-to-end content generation (images, videos, captions, hashtags)
> - Multi-stage quality assessment with AI judges
> - Queue management and publishing workflow
> - Complete database architecture and error handling
> - Music selection and analysis (mood matching, BPM detection, beat-sync via librosa)
> - Hashtag generation using 5-slot organic framework with visual context awareness
>
> **Modified for GDPR Compliance:**
> - **Performance tracking loop:** Platform analytics collection is currently paused due to GDPR considerations. The continuous learning system operates using **manual training data** in place of automated social media metrics. All feedback loops remain functional with human-curated quality assessments.
>
> **Under Active Development:**
> - Post-generation video analysis for improved hashtag relevance
> - Video quality assessment refinement

---

## Document Purpose
This document provides comprehensive Mermaid flowchart specifications for an AI-powered social media content creation and publishing pipeline. Each section includes visual flowcharts with brief technical explanations demonstrating end-to-end automation from concept to publication.

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Prompt Generation & Evaluation Pipeline](#2-prompt-generation--evaluation-pipeline)
3. [Image Generation Pipeline](#3-image-generation-pipeline)
4. [Video Generation Pipeline](#4-video-generation-pipeline)
5. [Quality Assessment System](#5-quality-assessment-system)
6. [Text Generation System](#6-text-generation-system)
7. [Queue Management & Publishing](#7-queue-management--publishing)
8. [Performance Tracking & Learning Loop](#8-performance-tracking--learning-loop)
9. [Google Sheets Integration](#9-google-sheets-integration)
10. [Slack Notifications](#10-slack-notifications)
11. [API & Tool Reference](#11-api--tool-reference)
12. [Database Schemas](#12-database-schemas)
13. [Error Handling & Retry Logic](#13-error-handling--retry-logic)

---

## 1. SYSTEM OVERVIEW

### 1.1 High-Level Pipeline Flow

```mermaid
graph TB
    Start([User Initiates Content Creation])

    Start --> ThemeSelection[Theme Selection & Mixing]
    ThemeSelection --> PromptGen[Prompt Generation]
    PromptGen --> PromptEval{Prompt Quality Gate}
    PromptEval -->|Pass| Reformat[Prompt Reformatting]
    PromptEval -->|Fail| PromptGen

    Reformat --> ContentType{Content Type?}
    ContentType -->|Image| ImageGen[Image Generation]
    ContentType -->|Video| VideoGen[Video Generation]

    ImageGen --> ImageQuality{Image Quality Gate}
    VideoGen --> VideoQuality{Video Quality Gate}

    ImageQuality -->|Pass| TextGen[Caption & Hashtag Generation]
    ImageQuality -->|Reject| ImageGen
    VideoQuality -->|Pass| TextGen
    VideoQuality -->|Reject| VideoGen

    TextGen --> QueueGen[Queue File Generation]
    QueueGen --> SheetSync[Google Sheets Sync]
    QueueGen --> TaskScheduler[Windows Task Scheduler]
    TaskScheduler --> SlackTask[Slack: Task Scheduled Alert]
    QueueGen --> InstaPub[Social Media Publisher]

    InstaPub --> Posted{Post Success?}
    Posted -->|Yes| SlackSuccess[Slack: Success Alert]
    Posted -->|No| SlackFail[Slack: Failure Alert]
    SlackSuccess --> Performance[Performance Tracking]
    SlackFail --> ErrorLog[Error Logging]
    ErrorLog --> Retry{Retry?}
    Retry -->|Yes| InstaPub
    Retry -->|No| ManualReview[Manual Review Required]

    Performance --> Insights[Collect Platform Analytics]
    Insights --> Learning[Update Training Weights]
    Learning -.->|Improves Future Content| PromptGen
```

**System:** End-to-end AI content pipeline with continuous learning from real engagement metrics.

**Entry Point:** `main.py`

**Databases:** `content_pipeline.db` | `video_pipeline.db` | `photo_learning_db` | `<database_folder>/account_a.db` | `<database_folder>/account_b.db`

**APIs:** OpenAI GPT-4/4o | Image Generation | Video Generation | Platform Publishing | Analytics | Google Drive/Sheets

---

## 2. PROMPT GENERATION & EVALUATION PIPELINE

### 2.1 Theme Selection & Prompt Pipeline

```mermaid
graph TB
    ThemeStart([Theme Selection])

    ThemeStart --> ThemeMixer[Theme Mixer Agent<br/>theme_mixer_agent.py]
    ThemeMixer -->|Load| ThemeYAML[YAML Theme Files<br/><evaluation_module>/themes/definitions/*.yaml]
    ThemeYAML --> ThemeRegistry[(ThemeRegistry)]

    ThemeMixer --> MixDecision{Mix Themes?}
    MixDecision -->|Yes| GPTMix[GPT-4 Theme Mixing<br/>Resolve conflicts & merge requirements]
    MixDecision -->|No| SingleTheme[Use Single Theme]

    GPTMix --> ValidateMix{Compatible?}
    ValidateMix -->|Yes| MergedTheme[Merged Theme Requirements]
    ValidateMix -->|No| ThemeMixer

    SingleTheme --> MergedTheme
    MergedTheme --> CreatePrompts[Create Prompts<br/>create_prompts.py]

    CreatePrompts --> ParseReqs[Parse Requirements<br/>Keywords, Style, Lighting, Mood]
    ParseReqs --> BuildPrompt[Construct Prompt<br/>Subject + Style + Technical]
    BuildPrompt --> SavePrompt[(DB: generated_prompts)]

    SavePrompt --> PromptJudge[Prompt Judge<br/>prompt_judge_gpt.py]
    PromptJudge --> GPTEval[GPT-4 Evaluation<br/>Score Theme Alignment<br/>Keyword Coverage<br/>Coherence<br/>Visual Clarity]

    GPTEval --> ScoreCheck{Score?}
    ScoreCheck -->|Pass >= 7.0| SaveApproval[(DB: Pass<br/>prompt_evaluations)]
    ScoreCheck -->|Improvement 5-6| Feedback[Get Improvement Suggestions]
    ScoreCheck -->|Fail < 5| SaveRejection[(DB: Fail<br/>prompt_evaluations)]

    Feedback --> AutoRefine[Auto-refine Prompt<br/>Max 2 attempts]
    AutoRefine --> PromptJudge
    SaveRejection --> CreatePrompts

    SaveApproval --> Reformatter[Reformatter<br/>reformatter.py]
    Reformatter --> GPTReformat[GPT-4 Prompt Optimization<br/>API-Specific Formatting]
    GPTReformat --> APIFormat{Target API?}

    APIFormat -->|Image| ImageAPIPrompt[Image API Format<br/>Comma-separated<br/>Max 200 chars<br/>aspect_ratio 9x16]
    APIFormat -->|Video| VideoAPIPrompt[Video API Format<br/>Natural language<br/>Max 300 chars<br/>Motion descriptors]

    ImageAPIPrompt --> SaveReformatted[(DB: reformatted_prompts)]
    VideoAPIPrompt --> SaveReformatted

    SaveReformatted --> ContentGen([Continue to Content Generation])
```

**Implementation:**
- `<evaluation_module>/theme_mixer_agent.py` - AI theme mixing (GPT-4)
- `src/prompt_generation/create_prompts.py` - Prompt construction
- `<evaluation_module>/prompt_judge_gpt.py` - Quality Gate 1
- `<evaluation_module>/reformatter.py` - API-specific formatting

**Quality Gate 1:** Pass: >= 7.0/10 | Auto-refine: 5.0-6.9 (max 2 attempts) | Reject: < 5.0

---

## 3. IMAGE GENERATION PIPELINE

### 3.1 Image Generation & Storage

```mermaid
graph TB
    ImgStart([Reformatted Prompt - Image])

    ImgStart --> ImageGenAPI[Image Generation API<br/>image_generation_api.py]
    ImageGenAPI --> PrepareRequest[Prepare API Request]

    PrepareRequest --> RequestBody{Request Parameters}
    RequestBody --> Prompt[prompt reformatted_text]
    RequestBody --> AspectRatio[aspect_ratio 9x16]
    RequestBody --> NumImages[num_images 1]
    RequestBody --> Style[style_preset auto<br/>quality high]

    Prompt --> SendRequest[POST to generate endpoint<br/>Authorization Bearer token]
    AspectRatio --> SendRequest
    NumImages --> SendRequest
    Style --> SendRequest

    SendRequest --> CheckStatus{Status?}
    CheckStatus -->|202 Accepted| PollStatus[Poll Status Endpoint<br/>Interval 10 seconds]
    CheckStatus -->|Error| ErrorHandle1[Error Handler]

    PollStatus --> Wait[Wait 10 seconds]
    Wait --> StatusCheck{Status?}
    StatusCheck -->|Processing| PollStatus
    StatusCheck -->|Completed| DownloadImage[Download Image URL]
    StatusCheck -->|Failed| ErrorHandle1

    DownloadImage --> SaveLocal[Save to <image_generation_output>/<br/>filename prompt_id_timestamp.png]
    SaveLocal --> ExtractMeta[Extract Metadata<br/>PIL Resolution<br/>os File Size<br/>Format PNG or JPG]

    ExtractMeta --> SaveDB[(DB: generated_images<br/>image_id, prompt_id<br/>file_path, resolution<br/>file_size_bytes, format<br/>generation_time_seconds)]

    SaveDB --> UploadDrive[Upload to Google Drive<br/>gdrive_uploader.py]
    UploadDrive --> GDriveAPI[Google Drive API<br/>Folder Generated Images theme]
    GDriveAPI --> PublicURL[Get Public URL<br/>Permissions Anyone with link]
    PublicURL --> UpdateDB[(Update DB<br/>gdrive_url<br/>gdrive_file_id)]

    UpdateDB --> QualityGate([Continue to Quality Gate])

    ErrorHandle1 --> CheckRetry{Retry Count?}
    CheckRetry -->|< 3| RetryDelay[Wait 30 seconds<br/>Exponential backoff]
    CheckRetry -->|>= 3| LogFailure[(Log to DB - Failed<br/>Mark: download_failed)]
    RetryDelay --> SendRequest
    LogFailure --> ManualReview[Manual Review Queue]
```

**Implementation:**
- `src/image_generation/image_generation_api.py` - Single image generation
- `src/image_generation/mass_filler_pic_gen.py` - Bulk batch processing
- `src/image_generation/gdrive_uploader.py` - Google Drive storage

**Technical Specs:**
- Polling: 10s intervals, 5min max timeout
- Retry: Exponential backoff (30s, 60s, 120s), max 3 attempts
- Validation: Rejects files < 1KB (corruption detection)
- Storage: `<image_generation_output>/` → Google Drive (public URLs)

**Current API:** Replicate FLUX.1 Krea [dev]

---

## 4. VIDEO GENERATION PIPELINE

### 4.1a Video Generation Flow

```mermaid
graph TB
    VidStart([Reformatted Prompt - Video])

    VidStart --> VideoType{Generation Type?}
    VideoType -->|Text-to-Video| T2V[Text-to-Video<br/>vid_gen.py]
    VideoType -->|Image-to-Video| I2V[Image-to-Video<br/>google_drive_img2vid.py]

    T2V --> VideoGenAPI[Video Generation API]
    I2V --> SourceImage[Get Source Image<br/>Google Drive API<br/>Download to temp dir]
    SourceImage --> MotionPrompt[Generate Motion Prompt<br/>GPT-4o Vision analyzes image<br/>Suggests natural motion]
    MotionPrompt --> VideoGenAPI

    VideoGenAPI --> PrepVideoModel[Prepare AI Video Model Request<br/>Model ai-video-model-v2]
    PrepVideoModel --> VideoParams{Request Parameters}

    VideoParams --> VPrompt[prompt text or motion description]
    VideoParams --> VDuration[duration 5-10 seconds]
    VideoParams --> VFPS[fps 30]
    VideoParams --> VResolution[aspect_ratio 9x16<br/>resolution 1080x1920]
    VideoParams --> VCamera[camera_movement dynamic<br/>motion_strength 0.8]

    VPrompt --> SubmitVideo[Submit to Video Model<br/>Get job ID]
    VDuration --> SubmitVideo
    VFPS --> SubmitVideo
    VResolution --> SubmitVideo
    VCamera --> SubmitVideo

    SubmitVideo --> PollVideo[Poll Job Status<br/>Interval 30 seconds<br/>Max wait 15 minutes]

    PollVideo --> StatusCheck{Status?}
    StatusCheck -->|Starting/Processing| PollVideo
    StatusCheck -->|Succeeded| DownloadVideo[Download Video<br/>Extract URL from response]
    StatusCheck -->|Failed| ErrorHandle([See 4.1c Error Handling])

    DownloadVideo --> SaveLocalVid[Save Video File<br/><video_generation_output>/<br/>prompt_id_timestamp.mp4]
    SaveLocalVid --> ExtractVidMeta[Extract Metadata<br/>ffprobe Duration and Resolution<br/>FPS and Codec and Bitrate and File Size]

    ExtractVidMeta --> SaveVidDB[(DB: videos<br/>video_id, prompt_id<br/>file_path, duration_seconds<br/>resolution, fps, codec<br/>video_job_id)]

    SaveVidDB --> MoviePyEnhance{Enhance with<br/>MoviePy?}
    MoviePyEnhance -->|Yes| EnhanceFlow([See 4.1b Enhancement])
    MoviePyEnhance -->|No| QualityGateVid([Continue to Quality Gate])
```

---

### 4.1b MoviePy Enhancement Pipeline

```mermaid
graph TB
    EnhanceStart([Video Ready for Enhancement])

    EnhanceStart --> MoviePyAgent[MoviePy Reel Creator<br/>moviepy_reel_creator_agent.py]

    MoviePyAgent --> MusicSelect[Music Selection<br/>music_selector_agent.py<br/>Match mood to library]
    MusicSelect --> MusicAnalysis[Music Analysis<br/>music_analysis_agent.py<br/>Detect beats & BPM]

    MusicAnalysis --> BeatDetection[Beat Detection<br/>librosa tempo and beat_frames<br/>RMS energy levels<br/>Segment intro verse chorus]
    BeatDetection --> SaveMusicMeta[(DB: music_metadata<br/>music_id, video_id<br/>bpm, beat_timestamps<br/>energy_levels, mood)]

    SaveMusicMeta --> SyncTransitions[Beat-Synced Transitions<br/>Align effects to beat timestamps<br/>Types: fade, zoom, slide]
    SyncTransitions --> AddTextOverlay[Add Text Overlays<br/>GPT-4o suggests moments<br/>2-3 short phrases 2-5 words<br/>Sync to beats]
    AddTextOverlay --> MixAudio[Mix Audio<br/>Music: 100%<br/>Original audio: 20% if exists]

    MixAudio --> PlatformFormat[Platform Content Formatting<br/>9:16 aspect ratio<br/>30 fps, H.264 codec<br/>AAC audio, 128k bitrate<br/>CRF: 23]

    PlatformFormat --> ExportEnhanced[Export Enhanced Reel<br/><enhanced_video_output>/<br/>video_id_enhanced.mp4]
    ExportEnhanced --> UpdateVidDB[(Update DB:<br/>has_music: true<br/>music_id<br/>has_text_overlays: true<br/>enhanced: true)]
    UpdateVidDB --> QualityGateVid([Continue to Quality Gate])
```

---

### 4.1c Video Error Handling

```mermaid
graph TB
    ErrorStart([Video Generation Failed])

    ErrorStart --> ClassifyError{Error Type?}
    ClassifyError -->|NSFW Detected| RejectPrompt[Mark prompt: nsfw_rejected<br/>Do NOT retry]
    ClassifyError -->|Model Overload| RetryDelay2[Wait 5 minutes<br/>Max 3 retries]
    ClassifyError -->|Timeout > 15min| CancelPrediction[Cancel prediction<br/>Retry with simpler prompt]
    ClassifyError -->|Other| CheckRetry2{Retry Count?}

    RetryDelay2 --> SubmitVideo[Retry Video Submission]
    CancelPrediction --> SubmitVideo
    CheckRetry2 -->|< 3| RetryDelay2
    CheckRetry2 -->|>= 3| FallbackImage[Fallback to Image Generation]

    RejectPrompt --> LogNSFW[(Log NSFW rejection<br/>Review prompt)]
    FallbackImage --> ImgPipeline([Image Generation Pipeline])
```

**Implementation:**
- `src/video_generation/vid_gen.py` - Text-to-video generation
- `src/video_generation/google_drive_img2vid.py` - Image-to-video (GPT-4o motion prompts)
- `src/agents/moviepy_reel_creator_agent.py` - Enhancement engine
- `src/agents/music_analysis_agent.py` - Beat detection (librosa)
- `src/agents/music_selector_agent.py` - Mood-based music selection

**Technical Specs:**
- Polling: 30s intervals, 15min max timeout
- Formats: Text-to-video | Image-to-video
- Enhancement: Beat-synced music/transitions/text overlays
- Output: `<video_generation_output>/` (raw) | `<enhanced_video_output>/` (enhanced)
- Platform format: 9:16, 30fps, H.264, AAC 128k, CRF 23

**Error Handling:**
- NSFW: Permanent rejection (no retry)
- Model overload: 5min wait, max 3 retries
- Timeout: Fallback to image generation after 3 attempts

**Current API:** Replicate Kling 2.1

---

## 5. QUALITY ASSESSMENT SYSTEM

### 5.1a Photo Judge Flow

```mermaid
graph TB
    QualityStart([Generated Content])

    QualityStart --> ContentCheck{Content Type?}
    ContentCheck -->|Image| PhotoJudge[Photo Judge<br/>photo_quality_judge.py]
    ContentCheck -->|Video| VideoJudge([See 5.1b Video Judge])

    PhotoJudge --> LoadWeights1[Load Training Weights]
    LoadWeights1 --> WeightFiles1{Weight Files}
    WeightFiles1 --> TrainedWeights[hashtag_weights.json<br/>Historical training data]
    WeightFiles1 --> VisualWeights[visual_hashtag_weights.json<br/>Visual correlations]
    WeightFiles1 --> PhotoPatterns[authentic_camera_patterns.json<br/>Authentic aesthetic]

    TrainedWeights --> GPTVision1[GPT-4o Vision Analysis]
    VisualWeights --> GPTVision1
    PhotoPatterns --> GPTVision1

    GPTVision1 --> AnalyzeImage{Scoring Dimensions}
    AnalyzeImage --> SceneQuality[Scene Quality: 0-10<br/>Clarity, artifacts, realism]
    AnalyzeImage --> MoodAlign[Mood Alignment: 0-10<br/>Theme match, emotional tone]
    AnalyzeImage --> LightingScore[Lighting Quality: 0-10<br/>Natural, soft, golden hour]
    AnalyzeImage --> CompositionScore[Composition: 0-10<br/>Rule of thirds, balance]
    AnalyzeImage --> SubjectDetail[Subject Detail: 0-10<br/>Wildlife, landscape, aerial, architecture authenticity]

    SceneQuality --> CalcOverall1[Calculate Weighted Overall<br/>Apply learned patterns]
    MoodAlign --> CalcOverall1
    LightingScore --> CalcOverall1
    CompositionScore --> CalcOverall1
    SubjectDetail --> CalcOverall1

    CalcOverall1 --> PhotoDecision{Score >= 6.0?}
    PhotoDecision -->|Pass| SavePhotoPass[(DB: evaluations - PASS<br/>photo_learning_db)]
    PhotoDecision -->|Reject| GenFeedback1[Generate Detailed Feedback<br/>Improvement suggestions]

    GenFeedback1 --> SavePhotoReject[(DB: evaluations - REJECT)]
    SavePhotoReject --> ReturnToGen1[Return to Image Generation<br/>with feedback]

    SavePhotoPass --> PredictEngagement[Predict Engagement<br/>Compare to successful posts]
    PredictEngagement --> NextStage([Continue to Text Generation])
```

---

### 5.1b Video Judge Flow

```mermaid
graph TB
    VideoStart([Video Content for Evaluation])

    VideoStart --> VideoJudge[Video Judge<br/>video_quality_judge.py]
    VideoJudge --> ExtractFrames[Extract Key Frames<br/>FFmpeg: 0%, 25%, 50%, 75%, 100%]
    ExtractFrames --> GPTVision2[GPT-4o Vision<br/>Multi-Frame Analysis]

    GPTVision2 --> VideoScoring{Scoring Dimensions}
    VideoScoring --> TechnicalQuality[Technical Quality: 0-10<br/>Resolution, smoothness, clarity]
    VideoScoring --> EngagementPotential[Engagement Potential: 0-10<br/>Hook, pacing, rewatchability]
    VideoScoring --> ThemeCoherence[Theme Coherence: 0-10<br/>Visual consistency with theme]
    VideoScoring --> MotionQuality[Motion Quality: 0-10<br/>Fluid motion, no warping]

    TechnicalQuality --> TechValidation[Technical Validation<br/>Resolution: 1080x1920<br/>Duration: 3-90s<br/>Codec: H.264<br/>Size: < 100MB]
    EngagementPotential --> CalcOverall2[Calculate Overall Score]
    ThemeCoherence --> CalcOverall2
    MotionQuality --> CalcOverall2
    TechValidation --> CalcOverall2

    CalcOverall2 --> VideoDecision{Score >= 6.0 AND<br/>Tech validation pass?}
    VideoDecision -->|Pass| SaveVideoPass[(DB: video_quality_scores - PASS)]
    VideoDecision -->|Reject| GenFeedback2[Generate Detailed Feedback<br/>Frame-specific issues]

    GenFeedback2 --> SaveVideoReject[(DB: video_quality_scores - REJECT)]
    SaveVideoReject --> ReturnToGen2[Return to Video Generation<br/>with feedback]

    SaveVideoPass --> NextStage([Continue to Text Generation])
```

**Implementation:**
- `<evaluation_module>/photo_quality_judge.py` - Image scoring (GPT-4o Vision, 5 dimensions)
- `<evaluation_module>/video_quality_judge.py` - Video scoring (multi-frame analysis)
- `src/video_generation/reel_quality_gate.py` - Technical validation

**Quality Gate 2 Criteria:**
- **Images:** Scene | Mood | Lighting | Composition | Style (weighted by training data)
- **Videos:** Technical | Engagement | Brand | Motion + validation (1080x1920, 3-90s, H.264, <100MB)
- **Threshold:** >= 6.0/10 overall
- **Training Data:** `hashtag_weights.json` | `visual_hashtag_weights.json` | `authentic_camera_patterns.json` | `<evaluation_module>/image_training_data/`

**Pass Rate:** 60-70% first attempt | 85-90% after feedback refinement

---

## 6. TEXT GENERATION SYSTEM

### 6.1a Caption Generation Flow

```mermaid
graph TB
    TextStart([Approved Content])

    TextStart --> VisualAnalysis[GPT-4o Vision<br/>Extract Visual Context]
    VisualAnalysis --> VisualContext{Visual Elements}
    VisualContext --> Scene[Scene: wilderness, terrain, skyline]
    VisualContext --> Objects[Objects: wildlife, terrain, structures]
    VisualContext --> Colors[Colors: warm, cool, vibrant]
    VisualContext --> Mood[Mood: serene, dramatic, majestic]
    VisualContext --> Subjects[Subjects: animals, formations, buildings]

    Scene --> CaptionGen[Caption Generator<br/>video_caption_generator.py]
    Objects --> CaptionGen
    Colors --> CaptionGen
    Mood --> CaptionGen
    Subjects --> CaptionGen

    CaptionGen --> AccountStyle{Account?}
    AccountStyle -->|Account A| PremiumStyle[Premium Style<br/>Aspirational, sophisticated<br/>First-person narrative<br/>100-150 chars optimal]
    AccountStyle -->|Account B| CasualStyle[Casual Style<br/>Friendly, relatable<br/>Conversational tone<br/>Authentic voice]

    PremiumStyle --> CaptionGPT[GPT-4o Caption Generation<br/>Temperature: 0.7]
    CasualStyle --> CaptionGPT

    CaptionGPT --> CaptionStructure[Caption Structure]
    CaptionStructure --> Hook[1. Hook: First 1-2 sentences<br/>Grab attention immediately]
    CaptionStructure --> Body[2. Body: 2-3 sentences<br/>Micro-story, emotional connection]
    CaptionStructure --> CTA[3. CTA: Optional call-to-action<br/>Subtle engagement prompt]

    Hook --> CaptionValidation{Quality Check?}
    Body --> CaptionValidation
    CTA --> CaptionValidation

    CaptionValidation -->|Pass| SaveCaption[(DB: video_captions<br/>caption_text, structure)]
    CaptionValidation -->|Revise| CaptionGPT

    SaveCaption --> HashtagFlow([See 6.1b Hashtag Generation])
```

---

### 6.1b Hashtag Generation Flow

```mermaid
graph TB
    HashtagStart([Caption Complete])

    HashtagStart --> HashtagGen[Hashtag Generator<br/>video_hashtag_generator.py]

    HashtagGen --> LoadHashtagWeights[Load Performance Weights]
    LoadHashtagWeights --> HashtagWeights{Weight Files}
    HashtagWeights --> PerfData[hashtag_weights.json<br/>Historical engagement rates<br/>Reach metrics per hashtag]
    HashtagWeights --> VisualCorr[visual_hashtag_weights.json<br/>Visual element correlations<br/>Scene-to-tag mappings]

    PerfData --> VisualMatch[Visual Hashtag Correlator<br/>Match visual elements to tags]
    VisualCorr --> VisualMatch

    VisualMatch --> HashtagStrategy[Apply Strategy Mix]
    HashtagStrategy --> Trending[30% Trending<br/>6-9 tags<br/>High volume > 100K posts<br/>Broad reach]
    HashtagStrategy --> Niche[40% Niche<br/>8-12 tags<br/>Medium volume 10K-100K<br/>Target audience, higher engagement]
    HashtagStrategy --> Brand[20% Brand<br/>4-6 tags<br/>Account-specific branding<br/>Brand lifestyle tags]
    HashtagStrategy --> UltraNiche[10% Ultra-Niche<br/>2-3 tags<br/>Low volume < 10K<br/>Long-tail, hyper-targeted]

    Trending --> HashtagGPT[GPT-4 Hashtag Selection<br/>Temperature: 0.5<br/>Total: 20-30 tags]
    Niche --> HashtagGPT
    Brand --> HashtagGPT
    UltraNiche --> HashtagGPT

    HashtagGPT --> HashtagJudge[Hashtag Judge<br/>hashtag_judge_visual.py]
    HashtagJudge --> ScoreRelevance[Score Visual Relevance<br/>Check: Visual alignment 0-1<br/>Performance history<br/>Strategy distribution]

    ScoreRelevance --> HashtagDecision{Score >= 0.5 AND<br/>Distribution correct?}
    HashtagDecision -->|Pass| SaveHashtags[(DB: video_hashtags<br/>hashtags JSON array<br/>category breakdown)]
    HashtagDecision -->|Revise| ReplaceHashtags[Replace Low-Scoring Tags<br/>Rebalance distribution]
    ReplaceHashtags --> HashtagGPT

    SaveHashtags --> FinalPackage[Complete Post Package]
    FinalPackage --> QueueStage([Continue to Queue Generation])
```

**Implementation:**
- `src/text_content_generation/video_caption_generator.py` - Caption generation (GPT-4o Vision)
- `src/text_content_generation/video_hashtag_generator.py` - Strategic hashtag selection
- `<evaluation_module>/hashtag_judge_visual.py` - Visual relevance scoring
- `<evaluation_module>/caption_judge_vision.py` - Caption quality gate

**Caption Styles:**
- **Account A:** Premium (aspirational, sophisticated, first-person, 100-150 chars)
- **Account B:** Casual (friendly, relatable, conversational, authentic)
- **Structure:** Hook (1-2 sentences) + Body (2-3 sentences) + CTA (optional)

**Hashtag Strategy (20-30 tags):**
- 30% Trending (6-9 tags, >100K posts, broad reach)
- 40% Niche (8-12 tags, 10K-100K posts, target audience)
- 20% Brand (4-6 tags, account-specific)
- 10% Ultra-Niche (2-3 tags, <10K posts, hyper-targeted)
- Weighted by performance data from `hashtag_weights.json` + `visual_hashtag_weights.json`

---

## 7. QUEUE MANAGEMENT & PUBLISHING

### 7.1a Queue Generation Flow

```mermaid
graph TB
    QueueStart([Complete Post Package])

    QueueStart --> Scheduler[Reel Scheduler<br/>reel_scheduler.py]
    Scheduler --> AnalyzePatterns[Analyze Engagement Patterns<br/>Best posting times<br/>Audience activity peaks]

    AnalyzePatterns --> AssignTime[Assign Optimal Time<br/>Based on historical data<br/>Avoid conflicts]

    AssignTime --> GenerateQueue[Generate Queue Files]
    GenerateQueue --> QueueFormats{Dual Format Output}

    QueueFormats --> JSONQueue[JSON Format<br/>queue_TIMESTAMP.json<br/>Structured data]
    QueueFormats --> TXTQueue[TXT Format<br/>queue_TIMESTAMP.txt<br/>Human-readable]

    JSONQueue --> QueueStructure{Queue Structure}
    TXTQueue --> QueueStructure

    QueueStructure --> FileName[filename - video_id.mp4]
    QueueStructure --> Caption[caption - text]
    QueueStructure --> Hashtags[hashtags - array]
    QueueStructure --> ScheduledTime[scheduled_time - datetime<br/>CRITICAL Display only NOT enforced]
    QueueStructure --> Account[account - Account A or Account B]

    FileName --> SaveQueue[(Save Queue Files<br/><publishing_queue_folder>/<account>/)]
    Caption --> SaveQueue
    Hashtags --> SaveQueue
    ScheduledTime --> SaveQueue
    Account --> SaveQueue

    SaveQueue --> QueueDB[(DB: scheduled_reels<br/>video_pipeline.db)]

    SaveQueue --> TaskScheduler[Windows Task Scheduler<br/>create_instagram_tasks.py]
    TaskScheduler --> SlackTaskAlert[Slack: Task Scheduled Alert<br/>Task name, time, media file]

    QueueDB --> SheetsOrPublish([See 7.1b Sheets Sync or 7.1c Publishing])
```

---

### 7.1b Google Sheets Sync (Optional)

```mermaid
graph TB
    SheetsStart([Queue Files Ready])

    SheetsStart --> OptionalSheets{Sync to Google Sheets?}
    OptionalSheets -->|No| PublisherMenu([See 7.1c Publishing])
    OptionalSheets -->|Yes| SheetsSync[Google Sheets Integration<br/>google_sheets_sync.py]

    SheetsSync --> GDriveThumbnails[Upload Thumbnails to GCS<br/>Generate signed URLs 7-day expiry]
    GDriveThumbnails --> SheetsFormat[Format Spreadsheet<br/>Date - Time - Account<br/>Caption - Hashtags - Thumbnail]
    SheetsFormat --> UpdateSheets[Update Shared Calendar<br/>Team collaboration<br/>Comments and approvals]
    UpdateSheets --> RefreshDaily[Daily Refresh Task<br/>refresh_gcs_signed_urls.py<br/>REFRESH_GCS_DAILY.bat]

    RefreshDaily --> PublisherMenu
```

---

### 7.1c Publishing Flow

```mermaid
graph TB
    PublishStart([Ready to Publish])

    PublishStart --> PublisherMenu[Social Media Publisher<br/>social_media_publisher.py]

    PublisherMenu --> AccountSelect{Select Account}
    AccountSelect -->|Account A| AccountADB[Load Account A Database<br/><database_folder>/account_a.db]
    AccountSelect -->|Account B| AccountBDB[Load Account B Database<br/><database_folder>/account_b.db]

    AccountADB --> SafetyCheck[Safety Confirmation<br/>User must type account name<br/>Session timeout: 15 minutes]
    AccountBDB --> SafetyCheck

    SafetyCheck --> LoadQueue[Load Queue File<br/>JSON or TXT format]
    LoadQueue --> UploadGDrive[Upload Media to Google Drive<br/>Get public URL for platform]

    UploadGDrive --> CreateContainer[Create Media Container<br/>POST to media endpoint<br/>Platform Publishing API]

    CreateContainer --> ContainerReady{Container Status?}
    ContainerReady -->|Ready| PublishPost[Publish Post<br/>POST to media_publish endpoint<br/>CRITICAL Posts IMMEDIATELY]
    ContainerReady -->|Error| ErrorHandler[Error Handler]

    PublishPost --> PostSuccess{Success?}
    PostSuccess -->|Yes| SlackSuccessAlert[Slack: Success Alert<br/>Media type, caption preview]
    PostSuccess -->|No| SlackFailAlert[Slack: Failure Alert<br/>Error message, media path]

    SlackSuccessAlert --> SaveToPublishedDB[(DB: published_posts<br/>Account-specific database<br/>Platform ID and timestamp and metadata)]
    SlackFailAlert --> ErrorHandler

    SaveToPublishedDB --> UpdateQueueStatus[(Update Status<br/>DB: publishing_queue<br/>status: published)]

    UpdateQueueStatus --> NextInQueue{More in Queue?}
    NextInQueue -->|Yes| LoadQueue
    NextInQueue -->|No| SlackBulkSummary[Slack: Bulk Upload Summary<br/>Total, successful, failed counts]
    SlackBulkSummary --> PublishComplete[Publishing Complete]

    ErrorHandler --> LogError[(DB: posting_errors<br/>Error details, retry count)]
    LogError --> RetryDecision{Retry?}
    RetryDecision -->|Yes, < 3| WaitRetry[Wait 60 seconds<br/>Exponential backoff]
    WaitRetry --> CreateContainer
    RetryDecision -->|No| ManualReview[Mark for Manual Review]

    PublishComplete --> PerformanceTracking([Continue to Performance Tracking])
```

**Implementation:**
- `src/video_generation/reel_scheduler.py` - Queue generation (dual format: JSON + TXT)
- `publisher/social_media_publisher.py` - Publishing engine
- `<sheets_integration_folder>/google_sheets_sync.py` - Optional team calendar sync

**Queue Structure:**
- **Formats:** JSON (programmatic) + TXT (human-readable)
- **Fields:** filename | caption | hashtags[] | scheduled_time | account
- **Location:** `<publishing_queue_folder>/<account>/`

**Safety Features:**
- Account isolation: `<database_folder>/account_a.db` | `<database_folder>/account_b.db`
- Confirmations: Name verification + double confirmation
- Session timeout: 15 minutes
- Rate limiting: Platform API compliance
- Retry: Max 3 attempts, exponential backoff

---

## 8. PERFORMANCE TRACKING & LEARNING LOOP

### 8.1a Metrics Collection

```mermaid
graph TB
    TrackStart([Published Post])

    TrackStart --> WaitPeriod[Wait Period<br/>24-48 hours for meaningful data]
    WaitPeriod --> InsightsCollector[Insights Collector<br/>insights_collector.py]

    InsightsCollector --> PlatformAnalyticsAPI[Platform Analytics API<br/>Insights Endpoint<br/>GET media insights]

    PlatformAnalyticsAPI --> MetricsCollection{Collect Metrics}
    MetricsCollection --> Impressions[Impressions - Total views]
    MetricsCollection --> Reach[Reach - Unique accounts]
    MetricsCollection --> Engagement[Engagement<br/>Likes and comments<br/>Saves and shares]
    MetricsCollection --> ProfileVisits[Profile Visits<br/>From this post]
    MetricsCollection --> Demographics[Demographics<br/>Age and gender and location]

    Impressions --> SavePerformance[(DB: content_performance<br/>Time-series metrics)]
    Reach --> SavePerformance
    Engagement --> SavePerformance
    ProfileVisits --> SavePerformance
    Demographics --> SavePerformance

    SavePerformance --> HashtagBreakdown[Analyze Per-Hashtag Performance<br/>Which tags drove reach?]
    HashtagBreakdown --> SaveHashtagPerf[(DB: hashtag_performance<br/>Per-tag analytics)]

    SaveHashtagPerf --> ThemeBreakdown[Analyze Theme Performance<br/>Which themes engaged audience?]
    ThemeBreakdown --> SaveThemePerf[(DB: theme_performance<br/>Theme-level insights)]

    SaveThemePerf --> GenerateReports[Generate Reports<br/><insights_reports_folder>/<account>/reports/]
    GenerateReports --> CollectionSummary[collection_summary_TIMESTAMP.json<br/>Overall stats]
    GenerateReports --> HashtagReport[hashtag_reports/<br/>Per-tag performance]

    CollectionSummary --> LearningLoop([See 8.1b Learning Loop])
    HashtagReport --> LearningLoop
```

---

### 8.1b Learning Loop

```mermaid
graph TB
    LearnStart([Performance Data Ready])

    LearnStart --> LearningLoop[Continuous Learning Loop<br/>continuous_learning_loop.py]

    LearningLoop --> CorrelationAnalysis{Correlation Analysis}
    CorrelationAnalysis --> ThemeCorr[Theme Performance<br/>Which themes perform best?]
    CorrelationAnalysis --> VisualCorr[Visual Elements<br/>Which visuals drive engagement?]
    CorrelationAnalysis --> HashtagCorr[Hashtag Effectiveness<br/>Which hashtags deliver reach?]
    CorrelationAnalysis --> CaptionCorr[Caption Patterns<br/>Which styles convert?]

    ThemeCorr --> WeightUpdates[Update Training Weights]
    VisualCorr --> WeightUpdates
    HashtagCorr --> WeightUpdates
    CaptionCorr --> WeightUpdates

    WeightUpdates --> UpdateHashtagWeights[Update:<br/>hashtag_weights.json<br/>New engagement rates<br/>Reach metrics]
    WeightUpdates --> UpdateVisualWeights[Update:<br/>visual_hashtag_weights.json<br/>Visual-tag correlations]
    WeightUpdates --> UpdateThemeWeights[Update:<br/>theme_performance table<br/>Theme success scores]

    UpdateHashtagWeights --> MergeManual[Merge with Manual Training<br/>training_data_processor.py<br/>Manual evaluations from GUI]
    UpdateVisualWeights --> MergeManual
    UpdateThemeWeights --> MergeManual

    MergeManual --> AdaptiveJudges[Update Adaptive Judges]
    AdaptiveJudges --> AdaptivePhoto[adaptive_photo_judge_system.py<br/>Learn from successful posts]
    AdaptiveJudges --> SelfLearning[self_learning_photo_judge.py<br/>Adjust scoring thresholds]
    AdaptiveJudges --> ThemeSpecific[theme_specific_adaptive_system.py<br/>Theme-based evaluation]

    AdaptivePhoto --> PatternRecognition{Pattern Recognition}
    SelfLearning --> PatternRecognition
    ThemeSpecific --> PatternRecognition

    PatternRecognition --> SuccessPatterns[Identify Success Patterns<br/>What's working?]
    PatternRecognition --> FailurePatterns[Flag Underperforming<br/>What's not working?]

    SuccessPatterns --> Recommendations[Generate Recommendations<br/>Theme suggestions<br/>Visual style guidance<br/>Hashtag adjustments]
    FailurePatterns --> Recommendations

    Recommendations --> UpdateSystemConfig[(DB: system_config<br/>content_pipeline.db<br/>Updated parameters)]

    UpdateSystemConfig --> FeedbackLoop[Feedback to Pipeline]
    FeedbackLoop -.->|Improves| PromptGeneration[Prompt Generation]
    FeedbackLoop -.->|Optimizes| ThemeSelection[Theme Selection]
    FeedbackLoop -.->|Raises Standards| QualityScoring[Quality Scoring]
    FeedbackLoop -.->|Refines| HashtagGeneration[Hashtag Generation]
```

**Implementation:**
- `publisher/insights_collector.py` - Metrics collection (Platform Analytics API, 24-48hr delay)
- `<evaluation_module>/continuous_learning_loop.py` - Correlation analysis → weight updates
- `<evaluation_module>/training_data_processor.py` - Automated + manual data merger
- `<evaluation_module>/adaptive_photo_judge_system.py` - Self-improving quality gates
- `<evaluation_module>/self_learning_photo_judge.py` - Dynamic threshold adjustment
- `<evaluation_module>/theme_specific_adaptive_system.py` - Theme-level optimization

**Metrics Collected:**
- Impressions | Reach | Engagement (likes, comments, saves, shares)
- Profile visits | Demographics | Time-series performance

**Learning Loop:** Performance data → Correlation analysis → Auto-update weights → Improved:
- Prompt generation
- Theme selection
- Quality scoring thresholds
- Hashtag selection strategy

**Training Data:**
- `hashtag_weights.json` - Engagement rates (auto-updated)
- `visual_hashtag_weights.json` - Visual correlations (auto-updated)
- `photo_learning_db` - Quality evaluations
- `<evaluation_module>/image_training_data/` - Manual examples (excellent/good/poor/bad)
- Reports: `<insights_reports_folder>/<account>/reports/`

---

## 9. GOOGLE SHEETS INTEGRATION

### 9.1a Initial Sync Flow

```mermaid
graph TB
    SheetsStart([Queue Files Generated])

    SheetsStart --> SheetsSync[Google Sheets Sync<br/>google_sheets_sync.py]
    SheetsSync --> LoadConfig[Load Configuration<br/>sheets_config.json<br/>Sheet IDs, mappings]

    LoadConfig --> AuthGoogle[Google OAuth2<br/>google_credentials.json<br/>Token refresh if needed]

    AuthGoogle --> PrepareData[Prepare Content Data]
    PrepareData --> ExtractQueue{Extract from Queue}
    ExtractQueue --> DateTime[Date & Time<br/>scheduled_time field]
    ExtractQueue --> AccountInfo[Account<br/>Account A or Account B]
    ExtractQueue --> CaptionText[Caption<br/>First 100 chars]
    ExtractQueue --> HashtagList[Hashtags<br/>Comma-separated]
    ExtractQueue --> MediaFile[Media File<br/>Image or video]

    DateTime --> PrepThumbnails[Prepare Thumbnails]
    AccountInfo --> PrepThumbnails
    CaptionText --> PrepThumbnails
    HashtagList --> PrepThumbnails
    MediaFile --> PrepThumbnails

    PrepThumbnails --> UploadGCS[Upload to Google Cloud Storage<br/>GCS bucket: content-thumbnails]
    UploadGCS --> GenerateSignedURL[Generate Signed URLs<br/>7-day expiry<br/>Public read access]

    GenerateSignedURL --> SaveMapping[(Save URL Mapping<br/>signed_url_mapping.json<br/>file_id -> signed_url)]

    SaveMapping --> FormatSheet[Format Spreadsheet Data]
    FormatSheet --> SheetStructure{Sheet Structure}

    SheetStructure --> ColDate[Column A: Date<br/>YYYY-MM-DD]
    SheetStructure --> ColTime[Column B: Time<br/>HH:MM]
    SheetStructure --> ColAccount[Column C: Account<br/>Account A/Account B icon]
    SheetStructure --> ColThumbnail[Column D: Thumbnail<br/>=IMAGE signed_url]
    SheetStructure --> ColCaption[Column E: Caption<br/>Text preview]
    SheetStructure --> ColHashtags[Column F: Hashtags<br/>Tag list]
    SheetStructure --> ColStatus[Column G: Status<br/>Scheduled/Published/Failed]

    ColDate --> BatchUpdate[Batch Update Request<br/>Google Sheets API<br/>Append or update rows]
    ColTime --> BatchUpdate
    ColAccount --> BatchUpdate
    ColThumbnail --> BatchUpdate
    ColCaption --> BatchUpdate
    ColHashtags --> BatchUpdate
    ColStatus --> BatchUpdate

    BatchUpdate --> ApplyFormatting[Apply Formatting<br/>Colors, borders, fonts<br/>Conditional formatting for status]

    ApplyFormatting --> RefreshFlow([See 9.1b Daily Refresh])
```

---

### 9.1b Daily Refresh & Collaboration

```mermaid
graph TB
    RefreshStart([Initial Sync Complete])

    RefreshStart --> SetPermissions[Set Sheet Permissions<br/>Team collaboration<br/>Comment, view, edit rights]

    SetPermissions --> EnableFeatures[Enable Features<br/>Comments, approvals<br/>Status updates<br/>Team notifications]

    EnableFeatures --> RefreshSchedule[Schedule Daily Refresh<br/>REFRESH_GCS_DAILY.bat<br/>Windows Task Scheduler]

    RefreshSchedule --> RefreshTask{Daily Refresh Task}
    RefreshTask --> CheckExpiry[Check URL Expiry<br/>< 24 hours remaining?]
    CheckExpiry -->|Yes| RegenerateURLs[Regenerate Signed URLs<br/>Extend for 7 more days]
    CheckExpiry -->|No| SkipRefresh[Skip Refresh]

    RegenerateURLs --> UpdateSheet[Update Sheet with New URLs]
    UpdateSheet --> LogRefresh[Log Refresh Activity<br/>Timestamp, count updated]

    SkipRefresh --> SheetsComplete[Sheets Sync Complete]
    LogRefresh --> SheetsComplete

    SheetsComplete --> TeamCollaboration[Team Collaboration Features]
    TeamCollaboration --> Comments[Add Comments<br/>Feedback, suggestions]
    TeamCollaboration --> Approvals[Content Approval<br/>Mark as approved/rejected]
    TeamCollaboration --> StatusTracking[Status Tracking<br/>Update publishing status]

    Comments --> NotifyTeam[Team Notifications<br/>Email alerts for changes]
    Approvals --> NotifyTeam
    StatusTracking --> NotifyTeam
```

**Implementation:**
- `<sheets_integration_folder>/google_sheets_sync.py` - Queue → Google Sheets sync
- `<sheets_integration_folder>/refresh_gcs_signed_urls.py` - Daily URL regeneration (7-day expiry)
- `<sheets_integration_folder>/REFRESH_GCS_DAILY.bat` - Windows Task Scheduler automation

**Sheet Structure:**
- Date | Time | Account | Thumbnail (GCS signed URL) | Caption | Hashtags | Status

**Configuration:**
- `sheets_config.json` - Sheet IDs, column mappings, GCS bucket
- `calendar_config.json` - Calendar settings
- `signed_url_mapping.json` - File ID → URL mappings
- `carousel_file_mapping.json` - Multi-image tracking

**Use Case:** Team collaboration, visual content calendar, status tracking, approval workflow

---

## 10. SLACK NOTIFICATIONS

### 10.1 Slack Notification Flow

```mermaid
graph TB
    SlackStart([Pipeline Events])

    SlackStart --> EventType{Event Type?}

    EventType -->|Task Created| TaskEvent[Windows Task Scheduler<br/>create_instagram_tasks.py]
    EventType -->|Post Success| SuccessEvent[Publishing Success<br/>instagram_simple_post.py]
    EventType -->|Post Failure| FailEvent[Publishing Failure<br/>instagram_simple_post.py]
    EventType -->|Bulk Complete| BulkEvent[Bulk Upload Complete<br/>instagram_simple_post_multiaccount.py]

    TaskEvent --> TaskNotify[notify_task_scheduled]
    SuccessEvent --> SuccessNotify[notify_instagram_success]
    FailEvent --> FailNotify[notify_instagram_failure]
    BulkEvent --> BulkNotify[notify_bulk_upload_complete]

    TaskNotify --> TaskPayload{Notification Content}
    TaskPayload --> TaskName[Task name]
    TaskPayload --> TaskTime[Scheduled execution time]
    TaskPayload --> TaskMedia[Media file path]

    SuccessNotify --> SuccessPayload{Notification Content}
    SuccessPayload --> SuccessType[Media type]
    SuccessPayload --> SuccessCaption[Caption preview]
    SuccessPayload --> SuccessID[Platform media ID]

    FailNotify --> VerifyAPI[Verify via Platform API<br/>Check if post actually exists]
    VerifyAPI --> RealFailure{Actually Failed?}
    RealFailure -->|Yes| SendFailure[Send Failure Alert]
    RealFailure -->|No| SkipAlert[Skip False Positive]

    SendFailure --> FailPayload{Notification Content}
    FailPayload --> FailError[Error message]
    FailPayload --> FailMedia[Media path]
    FailPayload --> FailType[Media type]

    BulkNotify --> BulkPayload{Notification Content}
    BulkPayload --> BulkTotal[Total items]
    BulkPayload --> BulkSuccess[Successful uploads]
    BulkPayload --> BulkFailed[Failed uploads]

    TaskName --> SlackAPI[Slack API<br/>chat.postMessage]
    TaskTime --> SlackAPI
    TaskMedia --> SlackAPI
    SuccessType --> SlackAPI
    SuccessCaption --> SlackAPI
    SuccessID --> SlackAPI
    FailError --> SlackAPI
    FailMedia --> SlackAPI
    FailType --> SlackAPI
    BulkTotal --> SlackAPI
    BulkSuccess --> SlackAPI
    BulkFailed --> SlackAPI

    SlackAPI --> BlockKit[Format with Block Kit<br/>Rich message formatting]
    BlockKit --> PostMessage[POST to Slack Channel]
    PostMessage --> Delivered[Notification Delivered]
```

**Implementation:**
- `src/notifications/slack_notifier.py` - Core Slack notification module
- `src/notifications/__init__.py` - Singleton accessor via `get_notifier()`

**Notification Types:**

| Type | Method | Trigger | Content |
|------|--------|---------|---------|
| Task Scheduled | `notify_task_scheduled()` | Windows Task created | Task name, time, media file |
| Post Success | `notify_instagram_success()` | Successful publish | Media type, caption preview |
| Post Failure | `notify_instagram_failure()` | Failed publish | Error message, media path |
| Bulk Complete | `notify_bulk_upload_complete()` | Bulk upload finished | Total, success, failed counts |

**Key Features:**
- Instagram API verification (prevents false failure alerts by checking if post exists)
- Rich formatting via Slack Block Kit
- Dual transport support (slack_sdk library with requests fallback)

**Integration Points:**
1. `instagram_publisher/create_instagram_tasks.py` - Task scheduling alerts
2. `instagram_publisher/instagram_simple_post.py` - Individual post success/failure
3. `instagram_publisher/instagram_simple_post_multiaccount.py` - Bulk upload summaries
4. `instagram_publisher/run_single_post.py` - Scheduled post execution alerts

---

## 11. API & TOOL REFERENCE

### 11.1 Content Generation APIs

```mermaid
graph TB
    ContentStart([Content Generation APIs])

    ContentStart --> OpenAIBox[OpenAI APIs]
    ContentStart --> ImageBox[Image Generation API]
    ContentStart --> VideoBox[Video Generation API]

    OpenAIBox --> GPT4[GPT-4<br/>Model: gpt-4]
    OpenAIBox --> GPT4Vision[GPT-4o Vision<br/>Model: gpt-4o]

    GPT4 --> GPT4Uses{Use Cases}
    GPT4Uses --> ThemeMix[Theme Mixing<br/>temperature 0.7]
    GPT4Uses --> PromptEval[Prompt Evaluation<br/>temperature 0.3]
    GPT4Uses --> Reformat[Reformatting<br/>temperature 0.5]
    GPT4Uses --> HashtagGen[Hashtag Generation<br/>temperature 0.5]

    GPT4Vision --> VisionUses{Use Cases}
    VisionUses --> ImageQuality[Image Quality<br/>temperature 0.2]
    VisionUses --> VideoQuality[Video Quality<br/>temperature 0.2]
    VisionUses --> Captions[Caption Generation<br/>temperature 0.7]
    VisionUses --> MotionPrompt[Motion Prompts<br/>temperature 0.6]

    ImageBox --> ImageAPI[image-generation-api.example.com]
    ImageAPI --> ImageParams{Parameters}
    ImageParams --> IPrompt[prompt: Max 200 chars]
    ImageParams --> IAspect[aspect_ratio: 9x16]
    ImageParams --> IQuality[quality: high<br/>num_images: 1]

    VideoBox --> VideoAPI[video-generation-api.example.com]
    VideoAPI --> VideoParams{Parameters}
    VideoParams --> VPrompt[prompt: Max 300 chars]
    VideoParams --> VDuration[duration: 5-10s]
    VideoParams --> VAspect[aspect_ratio: 9x16<br/>fps: 30]
    VideoParams --> VMotion[motion_strength: 0.8<br/>camera: dynamic]
```

---

### 11.2 Publishing & Storage APIs

```mermaid
graph TB
    PubStart([Publishing & Storage])

    PubStart --> PlatformBox[Platform Publishing API]
    PubStart --> GoogleBox[Google APIs]

    PlatformBox --> PlatformAPI[platform-api.example.com]
    PlatformAPI --> PlatformOps{Endpoints}
    PlatformOps --> CreateMedia[POST /media<br/>Create container]
    PlatformOps --> PublishMedia[POST /media_publish<br/>Publish content]
    PlatformOps --> GetMetrics[GET /insights<br/>Analytics]

    GoogleBox --> DriveAPI[Google Drive API v3]
    GoogleBox --> SheetsAPI[Google Sheets API v4]
    GoogleBox --> GCSAPI[Google Cloud Storage]

    DriveAPI --> DriveOps{Operations}
    DriveOps --> Upload[files.create<br/>Upload media]
    DriveOps --> Permissions[permissions.create<br/>Public access]
    DriveOps --> Search[files.list<br/>Search folders]

    SheetsAPI --> SheetsOps{Operations}
    SheetsOps --> BatchWrite[batchUpdate<br/>Write cells]
    SheetsOps --> ReadCells[values.get<br/>Read data]
    SheetsOps --> Format[batchUpdate<br/>Formatting]

    GCSAPI --> GCSOps{Operations}
    GCSOps --> UploadBlob[Upload blob<br/>Thumbnails]
    GCSOps --> SignedURL[Signed URL<br/>7-day expiry]
```

---

### 11.3 Current Implementation

**Image Generation:** Replicate FLUX.1 Krea [dev]

**Video Generation:** Replicate Kling 2.1

**Python Stack:**
`openai` | `replicate` | `requests` | `google-api-python-client` | `google-auth` | `moviepy` | `librosa` | `Pillow` | `ffmpeg-python` | `slack_sdk`

---

### 11.4 Rate Limits & Best Practices

| API | Rate Limit | Strategy |
|-----|------------|----------|
| OpenAI GPT-4 | 10K RPM (tier-based) | Parse rate limit headers, exponential backoff |
| OpenAI GPT-4o | 30K RPM (tier-based) | Parse rate limit headers, exponential backoff |
| Image Generation | 100-1000 req/day (provider-dependent) | Queue for next day if exhausted |
| Video Generation | Pay-per-use (provider-dependent) | No strict limits, cost management |
| Platform Publishing | 200-500 calls/hour per user | Respect cooldowns, session timeouts |
| Google Drive | 10M requests/day | Batch operations where possible |
| Google Sheets | 500 requests/100 seconds | Use batchUpdate for multi-cell writes |

---

## 12. DATABASE SCHEMAS

### 12.1 Content Generation Databases

`content_pipeline.db` - Core prompt and image generation workflow

```mermaid
graph TB
    PipelineDB[(content_pipeline.db)]

    PipelineDB --> Prompts[generated_prompts<br/>prompt_id PK<br/>theme_name<br/>prompt_text<br/>keywords_used JSON<br/>mandatory_elements JSON<br/>status, created_at]

    PipelineDB --> Evaluations[prompt_evaluations<br/>evaluation_id PK<br/>prompt_id FK<br/>theme_alignment_score<br/>keyword_coverage_score<br/>coherence_score<br/>overall_score<br/>decision, feedback]

    PipelineDB --> Reformatted[reformatted_prompts<br/>reformatted_id PK<br/>original_prompt_id FK<br/>reformatted_text<br/>target_api<br/>technical_parameters JSON<br/>character_count]

    PipelineDB --> Images[generated_images<br/>image_id PK<br/>prompt_id FK<br/>file_path, resolution<br/>file_size_bytes<br/>gdrive_url, gdrive_file_id<br/>status, created_at]

    PipelineDB --> Config[system_config<br/>config_key PK<br/>config_value JSON<br/>Auto-updated by learning loop]
```

---

### 12.2 Video & Enhancement Databases

`video_pipeline.db` - Video generation, captions, hashtags, and music integration

```mermaid
graph TB
    VideoDB[(video_pipeline.db)]

    VideoDB --> Videos[videos<br/>video_id PK<br/>prompt_id FK<br/>file_path, duration_seconds<br/>resolution, fps, codec<br/>video_job_id<br/>has_music, music_id<br/>has_text_overlays<br/>enhanced BOOLEAN]

    VideoDB --> Captions[video_captions<br/>caption_id PK<br/>video_id FK<br/>caption_text<br/>character_count<br/>hook, body, cta<br/>style, account<br/>quality_score]

    VideoDB --> Hashtags[video_hashtags<br/>hashtag_set_id PK<br/>video_id FK<br/>hashtags JSON array<br/>trending_hashtags JSON<br/>niche_hashtags JSON<br/>brand_hashtags JSON<br/>visual_relevance_scores JSON<br/>strategy_distribution JSON]

    VideoDB --> Music[music_metadata<br/>music_id PK<br/>video_id FK<br/>music_file_path<br/>bpm INTEGER<br/>beat_timestamps JSON<br/>energy_levels JSON<br/>optimal_start/end_time<br/>mood TEXT]

    VideoDB --> Quality[video_quality_scores<br/>score_id PK<br/>video_id FK<br/>technical_quality<br/>engagement_potential<br/>theme_coherence<br/>motion_quality<br/>overall_score<br/>passes_quality_gate<br/>rejection_reasons JSON]
```

---

### 12.3 Publishing & Performance Databases

`account_a.db` | `account_b.db` - Account-specific publishing, errors, and analytics

```mermaid
graph TB
    AccountDB[(Account Databases)]

    AccountDB --> Posts[published_posts<br/>post_id PK<br/>platform_media_id<br/>content_type<br/>caption, hashtags JSON<br/>posted_at<br/>gdrive_url<br/>queue_file_source]

    AccountDB --> Queue[publishing_queue<br/>queue_id PK<br/>content_id<br/>scheduled_time<br/>status<br/>retry_count<br/>last_attempt_at<br/>Tracks publish attempts]

    AccountDB --> Errors[posting_errors<br/>error_id PK<br/>queue_id FK<br/>error_type<br/>error_message<br/>error_details JSON<br/>occurred_at<br/>resolved BOOLEAN]

    AccountDB --> Performance[content_performance<br/>perf_id PK<br/>post_id FK<br/>impressions, reach<br/>likes, comments<br/>saves, shares<br/>profile_visits<br/>collected_at<br/>Time-series metrics]

    AccountDB --> HashtagPerf[hashtag_performance<br/>hashtag_perf_id PK<br/>post_id FK<br/>hashtag TEXT<br/>engagement_rate<br/>reach_contribution<br/>category<br/>Per-tag analytics]

    AccountDB --> ThemePerf[theme_performance<br/>theme_perf_id PK<br/>theme_name<br/>post_count<br/>avg_engagement_rate<br/>avg_reach<br/>success_score<br/>Theme-level insights]
```

---

### 12.4 Learning & Training Databases

`photo_learning_db` - Quality evaluations and manual training data

```mermaid
graph TB
    LearningDB[(photo_learning_db)]

    LearningDB --> Evals[evaluations<br/>evaluation_id PK<br/>content_id FK<br/>content_type<br/>scene_quality<br/>mood_alignment<br/>lighting_quality<br/>composition<br/>subject_detail<br/>overall_score<br/>visual_elements JSON<br/>strengths JSON<br/>weaknesses JSON<br/>predicted_engagement<br/>passes_quality_gate<br/>decision]

    LearningDB --> Training[training_data<br/>training_id PK<br/>content_id<br/>manual_score<br/>ai_score<br/>feedback_notes<br/>category<br/>excellent/good/poor/bad<br/>Manual quality assessments]
```

**Database Architecture:**
The pipeline uses 4 database types: (1) `content_pipeline.db` for prompts and images, (2) `video_pipeline.db` for video workflow, (3) `photo_learning_db` for training/evaluations, (4) Account-specific databases for publishing and analytics. Complete data separation between accounts. SQLite for portability.

**Key Relationships:**
- `prompts → reformatted_prompts → content → captions/hashtags → queue → published posts → performance`
- `videos → music_metadata` (1-to-1 if enhanced)
- `videos → video_quality_scores` (1-to-1 evaluation)
- `content` → `evaluations` (1:many, multi-judge scoring)
- `posts` → `content_performance` (1:many, time-series)
- `posts` → `hashtag_performance` (1:many, per-tag metrics)

**Database Files:**
- `<database_folder>/content_pipeline.db` - Main pipeline
- `<database_folder>/video_pipeline.db` - Video workflow
- `<database_folder>/photo_learning_db` - Training/evaluation data
- `<database_folder>/account_a.db` - Account A (premium)
- `<database_folder>/account_b.db` - Account B (standard)

**Management:**
- `src/database/database_connection.py` - Connection manager
- `src/database/migrate_add_metadata_column.py` - Migration: metadata
- `src/database/migrate_add_music_metadata.py` - Migration: music support

---

## 13. ERROR HANDLING & RETRY LOGIC

### 13.1 Error Classification (Overview)

```mermaid
graph TB
    ErrorStart([Error Encountered])

    ErrorStart --> ClassifyError{Error Type?}

    ClassifyError -->|API Failure| APIError[API Error Handler<br/>See Section 13.2]
    ClassifyError -->|Publishing| PublishError[Platform Error Handler<br/>See Section 13.3]
    ClassifyError -->|Infrastructure| InfraError[Infrastructure Error Handler<br/>See Section 13.4]
    ClassifyError -->|Content Rejection| ContentError[Content Error Handler<br/>See Section 13.5]

    APIError --> RetryLogic[Retry Logic]
    PublishError --> RetryLogic
    InfraError --> RetryLogic
    ContentError --> RetryLogic

    RetryLogic --> CheckRetryCount{Retry Count?}
    CheckRetryCount -->|< Max Retries| PerformRetry[Perform Retry<br/>Exponential backoff]
    CheckRetryCount -->|>= Max Retries| LogFailure[(Log to posting_errors<br/>Manual review)]

    PerformRetry --> Success{Success?}
    Success -->|Yes| Continue[Continue Pipeline]
    Success -->|No| ErrorStart
```

---

### 13.2 API Error Handling

```mermaid
graph TB
    APIStart([API Error])

    APIStart --> APIType{API Type?}

    APIType -->|OpenAI| OpenAIHandler[OpenAI Handler]
    APIType -->|Image Gen| ImageHandler[Image Gen Handler]
    APIType -->|Video Gen| VideoHandler[Video Gen Handler]

    OpenAIHandler --> OpenAIErrors{Error?}
    OpenAIErrors -->|429 Rate Limit| RateLimit[Parse reset time<br/>Wait exact duration<br/>Retry]
    OpenAIErrors -->|401 Unauthorized| InvalidKey[Verify API key<br/>Alert user<br/>Halt]
    OpenAIErrors -->|400 Bad Request| LogInvalid[Log request<br/>Skip item<br/>Continue]
    OpenAIErrors -->|500 Server| Backoff[Exponential backoff<br/>2s, 4s, 8s<br/>Max 3 retries]

    ImageHandler --> ImageErrors{Error?}
    ImageErrors -->|429 Rate Limit| QuotaWait[Queue for quota reset<br/>Tomorrow retry]
    ImageErrors -->|400 Invalid Prompt| RefinePrompt[Refine prompt<br/>Remove issues<br/>Retry once]
    ImageErrors -->|402 Payment| QuotaAlert[Alert: Quota exhausted<br/>Pause generation]
    ImageErrors -->|Generation Failed| RetryGen[Retry 3x<br/>Then mark failed]

    VideoHandler --> VideoErrors{Error?}
    VideoErrors -->|NSFW Detected| NSFWMark[Mark nsfw_rejected<br/>No retry<br/>Log for review]
    VideoErrors -->|Model Overloaded| ModelWait[Wait 5min<br/>Retry 3x<br/>Queue if persist]
    VideoErrors -->|Timeout 15min| CancelJob[Cancel job<br/>Simplify prompt<br/>Fallback to image]
    VideoErrors -->|Failed| CheckMsg[Check error type<br/>Retry if transient]
```

---

### 13.3 Platform Publishing Errors

```mermaid
graph TB
    PubStart([Publishing Error])

    PubStart --> PubType{Error Source?}

    PubType -->|Platform API| PlatformHandler[Platform Handler]
    PubType -->|Google API| GoogleHandler[Google Handler]

    PlatformHandler --> PlatformErrors{Error?}
    PlatformErrors -->|401 Access Token| RefreshToken[OAuth2 token refresh<br/>Retry once]
    PlatformErrors -->|429 Rate Limit| RateWait[Wait 1 hour<br/>Reduce frequency<br/>Review quality]
    PlatformErrors -->|400 Invalid Params| ValidateMedia[Validate URL<br/>Check caption length<br/>Fix and retry]
    PlatformErrors -->|403 Permissions| CheckPerms[Verify permissions<br/>content_publish<br/>Alert if missing]

    GoogleHandler --> GoogleErrors{Error?}
    GoogleErrors -->|401 Auth| RefreshGoogle[Refresh OAuth2<br/>Re-auth if expired<br/>Retry]
    GoogleErrors -->|403 Quota| QuotaReset[Wait quota reset<br/>Queue operations]
    GoogleErrors -->|404 Not Found| VerifyIDs[Verify file/sheet IDs<br/>Check config<br/>Alert user]
    GoogleErrors -->|500 Server| RetryGoogle[Backoff retry<br/>2s, 4s, 8s<br/>Max 3 attempts]
```

---

### 13.4 Infrastructure Errors

```mermaid
graph TB
    InfraStart([Infrastructure Error])

    InfraStart --> InfraType{Error Type?}

    InfraType -->|Network| NetworkHandler[Network Handler]
    InfraType -->|File Operation| FileHandler[File Handler]
    InfraType -->|Database| DBHandler[Database Handler]

    NetworkHandler --> NetCheck[Verify connection<br/>Ping test]
    NetCheck -->|Connected| NetRetry[Retry with backoff<br/>Max 3 attempts]
    NetCheck -->|Disconnected| NetWait[Wait for connection<br/>Alert user<br/>Pause]

    FileHandler --> FileErrors{Error?}
    FileErrors -->|Not Found| CheckPath[Verify path<br/>Log missing file]
    FileErrors -->|Permission Denied| CheckFilePerms[Check permissions<br/>UAC issues<br/>Run as admin]
    FileErrors -->|Disk Full| DiskAlert[Alert: Disk full<br/>Clean temp<br/>Halt]
    FileErrors -->|Corrupted| DetectCorrupt[Check file size < 1KB<br/>Re-generate content]

    DBHandler --> DBErrors{Error?}
    DBErrors -->|Locked| WaitUnlock[Wait unlock<br/>SQLite 5s timeout<br/>Retry transaction]
    DBErrors -->|Schema Error| RunMigrations[Run migrations<br/>migrate_*.py<br/>Verify version]
    DBErrors -->|Constraint Violation| LogConstraint[Log details<br/>Skip duplicate<br/>Continue]
    DBErrors -->|Corrupted| RestoreBackup[Attempt restore<br/>Check .backup files]
```

---

### 13.5 Content & Retry Strategy

```mermaid
graph TB
    ContentStart([Content Rejection])

    ContentStart --> ContentType{Rejection Reason?}

    ContentType -->|Quality Low| QualityFeedback[Return to generation<br/>AI feedback<br/>Max 3 attempts]
    ContentType -->|NSFW Content| NSFWSkip[Skip content<br/>Log detection<br/>No retry<br/>Review prompt]
    ContentType -->|Technical Invalid| TechFix[Fix technical<br/>Resolution/codec/format<br/>Retry once]

    QualityFeedback --> RetryDecision[Retry Decision]
    NSFWSkip --> Continue[Continue Pipeline]
    TechFix --> RetryDecision

    RetryDecision --> RetryCount{Attempt Count?}
    RetryCount -->|< 3| ApplyBackoff[Apply exponential backoff<br/>2s → 4s → 8s<br/>Retry operation]
    RetryCount -->|>= 3| LogError[(Log to posting_errors<br/>Error type + details<br/>Manual review queue)]

    ApplyBackoff --> Success{Success?}
    Success -->|Yes| Continue
    Success -->|No| ContentStart

    LogError --> ManualReview[Manual Review<br/>Admin intervention]
```

**Error Classification:**
- **API Errors:** OpenAI | Image Gen | Video Gen | Platform | Google (rate limits, quotas, token refresh)
- **Network:** Connection verification + exponential backoff (2s, 4s, 8s, max 3 attempts)
- **File Operations:** Missing files, permissions, disk space, corruption (< 1KB detection)
- **Database:** SQLite locks, migrations, constraint violations
- **Authentication:** OAuth2 token refresh
- **Content Rejection:** Return to generation with AI feedback (max 3 attempts)

**Retry Strategies:**
- Exponential backoff: 2s → 4s → 8s (transient errors)
- Rate limit: Parse reset time, wait exact duration
- Quota exhausted: Queue for next reset (daily/hourly)
- NSFW: No retry (permanent), log for refinement
- Network: Verify connection, retry with backoff, halt if persistent
- Max retries: 3 attempts → `posting_errors` table for manual review

**Error Logging:**
- Database: `posting_errors` table (error_type, message, details JSON, retry_count, resolved)
- Files: Component-specific logs in `logs/` directory
- User Alerts: Console output for critical errors requiring intervention

**Manual Review Queue:** Failed items after max retries go to manual review queue. Admin can inspect errors, fix issues, and retry manually via publisher menu.

---

