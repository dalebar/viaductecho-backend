package com.viaductecho.android.data.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize

@Parcelize
data class Article(
    val id: Int,
    val title: String,
    val link: String,
    val summary: String,
    val source: String,
    @SerializedName("source_type")
    val sourceType: String,
    @SerializedName("published_date")
    val publishedDate: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("image_url")
    val imageUrl: String?,
    @SerializedName("ai_summary")
    val aiSummary: String?,
    @SerializedName("extracted_content")
    val extractedContent: String?,
    val processed: Boolean? = null,
    @SerializedName("updated_at")
    val updatedAt: String? = null
) : Parcelable

@Parcelize
data class ArticlesResponse(
    val articles: List<Article>,
    val pagination: Pagination
) : Parcelable

@Parcelize
data class Pagination(
    val page: Int,
    @SerializedName("per_page")
    val perPage: Int,
    @SerializedName("total_items")
    val totalItems: Int,
    @SerializedName("total_pages")
    val totalPages: Int,
    @SerializedName("has_next")
    val hasNext: Boolean,
    @SerializedName("has_prev")
    val hasPrev: Boolean
) : Parcelable

@Parcelize
data class Source(
    val name: String,
    @SerializedName("article_count")
    val articleCount: Int,
    @SerializedName("processed_count")
    val processedCount: Int,
    @SerializedName("latest_article")
    val latestArticle: String?
) : Parcelable

@Parcelize
data class SourcesResponse(
    val sources: List<Source>,
    @SerializedName("total_sources")
    val totalSources: Int
) : Parcelable

// Health check response
@Parcelize
data class HealthResponse(
    val status: String,
    @SerializedName("total_articles")
    val totalArticles: Int?,
    @SerializedName("recent_articles_24h")
    val recentArticles24h: Int?,
    @SerializedName("database_connected")
    val databaseConnected: Boolean,
    val timestamp: String,
    val error: String? = null
) : Parcelable
