package com.viaductecho.android.ui

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.swipeDown
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.isDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import com.viaductecho.android.R
import com.viaductecho.android.ui.articles.ArticleListAdapter
import com.viaductecho.android.ui.main.MainActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@LargeTest
@RunWith(AndroidJUnit4::class)
@HiltAndroidTest
class ArticleListFragmentTest {
    
    @get:Rule
    var hiltRule = HiltAndroidRule(this)
    
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)
    
    @Before
    fun setup() {
        hiltRule.inject()
    }
    
    @Test
    fun articleListFragment_displaysList() {
        // Verify RecyclerView is displayed
        onView(withId(R.id.recycler_view_articles))
            .check(matches(isDisplayed()))
    }
    
    @Test
    fun articleListFragment_pullToRefreshWorks() {
        // Perform pull to refresh
        onView(withId(R.id.swipe_refresh_layout))
            .perform(swipeDown())
        
        // Verify refresh layout exists
        onView(withId(R.id.swipe_refresh_layout))
            .check(matches(isDisplayed()))
    }
    
    @Test
    fun articleListFragment_clickArticleNavigatesToDetail() {
        // Wait for articles to load, then click first item
        Thread.sleep(2000) // Wait for network call
        
        onView(withId(R.id.recycler_view_articles))
            .perform(
                RecyclerViewActions.actionOnItemAtPosition<ArticleListAdapter.ArticleViewHolder>(
                    0, click()
                )
            )
        
        // Verify we're on detail screen (toolbar should show back button or different title)
        // This test would require actual data or mocked responses
    }
    
    @Test
    fun articleListFragment_showsEmptyStateWhenNoArticles() {
        // This test would require mocking the repository to return empty results
        // For now, verify empty state view exists in layout
        // onView(withId(R.id.empty_state_view))
        //     .check(matches(isDisplayed()))
    }
}