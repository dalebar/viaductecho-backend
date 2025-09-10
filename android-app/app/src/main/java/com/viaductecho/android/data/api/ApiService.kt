package com.viaductecho.android.data.api

import com.viaductecho.android.data.models.*
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @GET("health")
    suspend fun getHealth(): Response<HealthResponse>

    @GET("api/v1/articles")
    suspend fun getArticles(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("source") source: String? = null,
        @Query("processed_only") processedOnly: Boolean = true
    ): Response<ArticlesResponse>

    @GET("api/v1/articles/{id}")
    suspend fun getArticleById(
        @Path("id") articleId: Int
    ): Response<Article>

    @GET("api/v1/articles/recent")
    suspend fun getRecentArticles(
        @Query("hours") hours: Int = 24,
        @Query("limit") limit: Int = 10
    ): Response<ArticlesResponse>

    @GET("api/v1/articles/search")
    suspend fun searchArticles(
        @Query("q") query: String,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20
    ): Response<ArticlesResponse>

    @GET("api/v1/sources")
    suspend fun getSources(): Response<SourcesResponse>
}
