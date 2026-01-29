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

![1. Flowchart](diagrams/1_SYSTEM_OVERVIEW.png)

**System:** End-to-end AI content pipeline with continuous learning from real engagement metrics.

**Entry Point:** `main.py`

**Databases:** `content_pipeline.db` | `video_pipeline.db` | `photo_learning_db` | `<database_folder>/account_a.db` | `<database_folder>/account_b.db`

**APIs:** OpenAI GPT-4/4o | Image Generation | Video Generation | Platform Publishing | Analytics | Google Drive/Sheets

---

## 2. PROMPT GENERATION & EVALUATION PIPELINE

### 2.1 Theme Selection & Prompt Pipeline

![2. Flowchart](diagrams/2_PROMPT_GENERATION__EVALUATION_.png)

**Implementation:**
- `<evaluation_module>/theme_mixer_agent.py` - AI theme mixing (GPT-4)
- `src/prompt_generation/create_prompts.py` - Prompt construction
- `<evaluation_module>/prompt_judge_gpt.py` - Quality Gate 1
- `<evaluation_module>/reformatter.py` - API-specific formatting

**Quality Gate 1:** Pass: >= 7.0/10 | Auto-refine: 5.0-6.9 (max 2 attempts) | Reject: < 5.0

---

## 3. IMAGE GENERATION PIPELINE

### 3.1 Image Generation & Storage

![3. Flowchart](diagrams/3_IMAGE_GENERATION_PIPELINE.png)

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

![4. Flowchart](diagrams/4_VIDEO_GENERATION_PIPELINE.png)

---

### 4.1b MoviePy Enhancement Pipeline

![4.1b Flowchart](diagrams/4_1b_MoviePy_Enhancement_Pipeline.png)

---

### 4.1c Video Error Handling

![4.1c Flowchart](diagrams/4_1c_Video_Error_Handling.png)

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

![5. Flowchart](diagrams/5_QUALITY_ASSESSMENT_SYSTEM.png)

---

### 5.1b Video Judge Flow

![5.1b Flowchart](diagrams/5_1b_Video_Judge_Flow.png)

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

![6. Flowchart](diagrams/6_TEXT_GENERATION_SYSTEM.png)

---

### 6.1b Hashtag Generation Flow

![6.1b Flowchart](diagrams/6_1b_Hashtag_Generation_Flow.png)

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

![7. Flowchart](diagrams/7_QUEUE_MANAGEMENT__PUBLISHING.png)

---

### 7.1b Google Sheets Sync (Optional)

![7.1b Flowchart](diagrams/7_1b_Google_Sheets_Sync_Optional.png)

---

### 7.1c Publishing Flow

![7.1c Flowchart](diagrams/7_1c_Publishing_Flow.png)

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

![8. Flowchart](diagrams/8_PERFORMANCE_TRACKING__LEARNING.png)

---

### 8.1b Learning Loop

![8.1b Flowchart](diagrams/8_1b_Learning_Loop.png)

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

![9. Flowchart](diagrams/9_GOOGLE_SHEETS_INTEGRATION.png)

---

### 9.1b Daily Refresh & Collaboration

![9.1b Flowchart](diagrams/9_1b_Daily_Refresh__Collaboration.png)

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

![10. Flowchart](diagrams/10_SLACK_NOTIFICATIONS.png)

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

![11. Flowchart](diagrams/11_API__TOOL_REFERENCE.png)

---

### 11.2 Publishing & Storage APIs

![11.2 Flowchart](diagrams/11_2_Publishing__Storage_APIs.png)

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

![11.3 Flowchart](diagrams/11_3_Current_Implementation.png)

---

### 12.2 Video & Enhancement Databases

`video_pipeline.db` - Video generation, captions, hashtags, and music integration

![12.2 Flowchart](diagrams/12_2_Video__Enhancement_Databases.png)

---

### 12.3 Publishing & Performance Databases

`account_a.db` | `account_b.db` - Account-specific publishing, errors, and analytics

![12.3 Flowchart](diagrams/12_3_Publishing__Performance_Databa.png)

---

### 12.4 Learning & Training Databases

`photo_learning_db` - Quality evaluations and manual training data

![12.4 Flowchart](diagrams/12_4_Learning__Training_Databases.png)

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

![13. Flowchart](diagrams/13_ERROR_HANDLING__RETRY_LOGIC.png)

---

### 13.2 API Error Handling

![13.2 Flowchart](diagrams/13_2_API_Error_Handling.png)

---

### 13.3 Platform Publishing Errors

![13.3 Flowchart](diagrams/13_3_Platform_Publishing_Errors.png)

---

### 13.4 Infrastructure Errors

![13.4 Flowchart](diagrams/13_4_Infrastructure_Errors.png)

---

### 13.5 Content & Retry Strategy

![13.5 Flowchart](diagrams/13_5_Content__Retry_Strategy.png)

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

