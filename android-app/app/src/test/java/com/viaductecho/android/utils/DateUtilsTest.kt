package com.viaductecho.android.utils

import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@RunWith(RobolectricTestRunner::class)
class DateUtilsTest {

    @Test
    fun `formatRelativeTime returns 'Just now' for recent date`() {
        // Given - A date 30 seconds ago
        val now = LocalDateTime.now()
        val recentDate = now.minusSeconds(30)
        val dateString = recentDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss+00:00"))

        // When
        val result = DateUtils.formatRelativeTime(dateString)

        // Then
        assertEquals("Just now", result)
    }

    @Test
    fun `formatRelativeTime returns minutes ago for recent minutes`() {
        // Given - A date 5 minutes ago
        val now = LocalDateTime.now()
        val fiveMinutesAgo = now.minusMinutes(5)
        val dateString = fiveMinutesAgo.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss+00:00"))

        // When
        val result = DateUtils.formatRelativeTime(dateString)

        // Then
        assertEquals("5m ago", result)
    }

    @Test
    fun `formatRelativeTime returns hours ago for recent hours`() {
        // Given - A date 3 hours ago
        val now = LocalDateTime.now()
        val threeHoursAgo = now.minusHours(3)
        val dateString = threeHoursAgo.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss+00:00"))

        // When
        val result = DateUtils.formatRelativeTime(dateString)

        // Then
        assertEquals("3h ago", result)
    }

    @Test
    fun `formatRelativeTime returns days ago for recent days`() {
        // Given - A date 2 days ago
        val now = LocalDateTime.now()
        val twoDaysAgo = now.minusDays(2)
        val dateString = twoDaysAgo.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss+00:00"))

        // When
        val result = DateUtils.formatRelativeTime(dateString)

        // Then
        assertEquals("2d ago", result)
    }

    @Test
    fun `formatRelativeTime returns formatted date for old dates`() {
        // Given - A date more than a week ago
        val oldDate = LocalDateTime.of(2024, 1, 15, 10, 30)
        val dateString = oldDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss+00:00"))

        // When
        val result = DateUtils.formatRelativeTime(dateString)

        // Then
        assertEquals("Jan 15, 2024", result)
    }

    @Test
    fun `formatRelativeTime returns empty string for null input`() {
        // When
        val result = DateUtils.formatRelativeTime(null)

        // Then
        assertEquals("", result)
    }

    @Test
    fun `formatRelativeTime returns empty string for blank input`() {
        // When
        val result = DateUtils.formatRelativeTime("   ")

        // Then
        assertEquals("", result)
    }

    @Test
    fun `formatDisplayDate returns formatted date and time`() {
        // Given
        val dateString = "2024-03-15T14:30:00+00:00"

        // When
        val result = DateUtils.formatDisplayDate(dateString)

        // Then
        // Note: Exact format may vary based on timezone, but should contain date and time
        assert(result.contains("Mar 15, 2024"))
        assert(result.contains("•"))
    }

    @Test
    fun `formatDisplayDate returns input for invalid date`() {
        // Given
        val invalidDate = "invalid-date"

        // When
        val result = DateUtils.formatDisplayDate(invalidDate)

        // Then
        assertEquals(invalidDate, result)
    }

    @Test
    fun `formatDisplayDate returns empty string for null input`() {
        // When
        val result = DateUtils.formatDisplayDate(null)

        // Then
        assertEquals("", result)
    }
}
