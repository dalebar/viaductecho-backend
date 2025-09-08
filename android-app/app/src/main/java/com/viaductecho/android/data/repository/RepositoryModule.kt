package com.viaductecho.android.data.repository

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import com.viaductecho.android.data.api.ApiService
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    
    @Provides
    @Singleton
    fun provideArticleRepository(apiService: ApiService): ArticleRepository {
        return ArticleRepository(apiService)
    }
}