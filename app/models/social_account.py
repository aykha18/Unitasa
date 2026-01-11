"""
Social media account models for client-facing platform
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class SocialAccount(Base):
    """Social media account connections for users"""
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # twitter, linkedin, medium, etc.
    account_id = Column(String(100), nullable=False)  # Platform-specific account ID
    account_username = Column(String(100), nullable=False)  # @username or handle
    account_name = Column(String(200))  # Display name
    profile_url = Column(String(500))  # Profile URL
    avatar_url = Column(String(500))  # Profile picture URL

    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # Account metadata
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    # Platform-specific settings
    platform_settings = Column(JSON, default=dict)  # Rate limits, features, etc.

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_synced_at = Column(DateTime)
    last_post_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="social_accounts")
    posts = relationship("SocialPost", back_populates="social_account", cascade="all, delete-orphan")
    engagements = relationship("Engagement", back_populates="social_account")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="social_account")

    def __repr__(self):
        return f"<SocialAccount(user_id={self.user_id}, platform={self.platform}, username={self.account_username})>"




class SocialPost(Base):
    """Individual social media posts"""
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)

    # Platform and post details
    platform = Column(String(50), nullable=False)
    platform_post_id = Column(String(100))  # Platform's post ID
    post_url = Column(String(500))  # Direct link to post

    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, video, thread
    media_urls = Column(JSON, default=list)  # For images/videos
    hashtags = Column(JSON, default=list)
    mentions = Column(JSON, default=list)

    # Status and scheduling
    status = Column(String(50), default="scheduled")  # scheduled, posted, failed
    scheduled_at = Column(DateTime)
    posted_at = Column(DateTime)
    failed_at = Column(DateTime)
    failure_reason = Column(Text)

    # Performance metrics
    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    clicks = Column(Integer, default=0)

    # AI generation metadata
    generated_by_ai = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    ai_model = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="social_posts")
    social_account = relationship("SocialAccount", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")

    def __repr__(self):
        return f"<SocialPost(id={self.id}, platform={self.platform}, status={self.status})>"


class Engagement(Base):
    """Social media engagement actions (likes, comments, follows)"""
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), index=True)

    # Target post/account details
    platform = Column(String(50), nullable=False)
    target_account_id = Column(String(100))  # Account that was engaged with
    target_account_username = Column(String(100))
    target_post_id = Column(String(100))  # Post that was engaged with
    target_post_url = Column(String(500))

    # Engagement details
    engagement_type = Column(String(50), nullable=False)  # like, comment, follow, share
    comment_text = Column(Text)  # For comments
    engagement_reason = Column(String(200))  # Why this engagement was made

    # AI generation metadata
    generated_by_ai = Column(Boolean, default=False)
    ai_prompt = Column(Text)

    # Status
    status = Column(String(50), default="completed")  # completed, failed, pending
    failed_at = Column(DateTime)
    failure_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="engagements")
    social_account = relationship("SocialAccount", back_populates="engagements")
    campaign = relationship("Campaign", back_populates="engagements")

    def __repr__(self):
        return f"<Engagement(id={self.id}, type={self.engagement_type}, platform={self.platform})>"


class ContentTemplate(Base):
    """Reusable content templates for different platforms and campaigns"""
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    platform = Column(String(50), nullable=False)  # twitter, linkedin, etc.
    template_type = Column(String(50), default="post")  # post, thread, comment

    # Template content
    template_text = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # Dynamic variables like {topic}, {name}

    # Usage metadata
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    success_rate = Column(Integer, default=0)  # Percentage

    # Tags and categorization
    tags = Column(JSON, default=list)
    category = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="content_templates")

    def __repr__(self):
        return f"<ContentTemplate(id={self.id}, name={self.name}, platform={self.platform})>"


class AnalyticsSnapshot(Base):
    """Daily analytics snapshots for performance tracking"""
    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=False, index=True)

    # Date and period
    snapshot_date = Column(DateTime, nullable=False, index=True)
    period = Column(String(20), default="daily")  # daily, weekly, monthly

    # Account metrics
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    # Post metrics
    posts_count = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)
    total_engagements = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)

    # Engagement metrics
    engagements_made = Column(Integer, default=0)
    engagement_rate = Column(Integer, default=0)  # Percentage * 100

    # Lead generation (if integrated)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)

    # Platform-specific data
    platform_data = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="analytics_snapshots")
    social_account = relationship("SocialAccount", back_populates="analytics_snapshots")

    def __repr__(self):
        return f"<AnalyticsSnapshot(date={self.snapshot_date}, account={self.social_account_id})>"