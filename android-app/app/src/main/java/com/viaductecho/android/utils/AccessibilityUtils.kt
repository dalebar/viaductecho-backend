package com.viaductecho.android.utils

import android.content.Context
import android.view.View
import android.view.accessibility.AccessibilityManager
import androidx.core.view.AccessibilityDelegateCompat
import androidx.core.view.ViewCompat
import androidx.core.view.accessibility.AccessibilityNodeInfoCompat

/**
 * Utility functions for improving accessibility throughout the app
 */
object AccessibilityUtils {

    /**
     * Check if accessibility services are enabled
     */
    fun Context.isAccessibilityEnabled(): Boolean {
        val accessibilityManager = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        return accessibilityManager.isEnabled
    }

    /**
     * Check if TalkBack or other screen readers are enabled
     */
    fun Context.isScreenReaderEnabled(): Boolean {
        val accessibilityManager = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        return accessibilityManager.isTouchExplorationEnabled
    }

    /**
     * Set up accessibility for article items
     */
    fun View.setupArticleAccessibility(
        title: String,
        source: String,
        publishedDate: String,
        hasImage: Boolean = true
    ) {
        val accessibilityText = buildString {
            append("Article: $title. ")
            append("Source: $source. ")
            if (publishedDate.isNotBlank()) {
                append("Published $publishedDate. ")
            }
            if (hasImage) {
                append("Has image. ")
            }
            append("Double tap to open.")
        }

        contentDescription = accessibilityText

        // Set up custom accessibility delegate for additional actions
        ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)

                info.addAction(
                    AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                        AccessibilityNodeInfoCompat.ACTION_CLICK,
                        "Read article"
                    )
                )
            }
        })
    }

    /**
     * Set up accessibility for buttons with enhanced descriptions
     */
    fun View.setupButtonAccessibility(
        label: String,
        description: String? = null,
        isEnabled: Boolean = true
    ) {
        val accessibilityText = buildString {
            append(label)
            if (!isEnabled) {
                append(", disabled")
            }
            description?.let { append(". $it") }
        }

        contentDescription = accessibilityText

        // Add role information
        ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.roleDescription = "Button"
            }
        })
    }

    /**
     * Set up accessibility for images with proper descriptions
     */
    fun View.setupImageAccessibility(
        description: String,
        isDecorative: Boolean = false
    ) {
        if (isDecorative) {
            // Mark decorative images as not important for accessibility
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        } else {
            contentDescription = description
            importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_YES

            ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
                override fun onInitializeAccessibilityNodeInfo(
                    host: View,
                    info: AccessibilityNodeInfoCompat
                ) {
                    super.onInitializeAccessibilityNodeInfo(host, info)
                    info.roleDescription = "Image"
                }
            })
        }
    }

    /**
     * Set up accessibility for loading states
     */
    fun View.setupLoadingAccessibility(message: String = "Loading") {
        contentDescription = message
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_YES

        // Announce loading state changes
        announceForAccessibility(message)
    }

    /**
     * Set up accessibility for error states
     */
    fun View.setupErrorAccessibility(errorMessage: String, hasRetry: Boolean = true) {
        val accessibilityText = buildString {
            append("Error: $errorMessage")
            if (hasRetry) {
                append(". Retry button available.")
            }
        }

        contentDescription = accessibilityText
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_YES

        // Announce error
        announceForAccessibility(accessibilityText)
    }

    /**
     * Set up heading accessibility for better navigation
     */
    fun View.setupHeadingAccessibility(headingLevel: Int = 1) {
        ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.isHeading = true
                info.roleDescription = "Heading level $headingLevel"
            }
        })
    }

    /**
     * Set up list accessibility with item counts
     */
    fun View.setupListAccessibility(itemCount: Int, listType: String = "list") {
        val description = "$listType with $itemCount items"
        contentDescription = description

        ViewCompat.setAccessibilityDelegate(this, object : AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.roleDescription = "List"
                info.setCollectionInfo(
                    AccessibilityNodeInfoCompat.CollectionInfoCompat.obtain(
                        itemCount, 1, false, AccessibilityNodeInfoCompat.CollectionInfoCompat.SELECTION_MODE_NONE
                    )
                )
            }
        })
    }
}
