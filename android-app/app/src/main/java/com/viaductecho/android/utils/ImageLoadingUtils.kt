package com.viaductecho.android.utils

import android.graphics.drawable.Drawable
import android.widget.ImageView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.DataSource
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.bumptech.glide.load.engine.GlideException
import com.bumptech.glide.load.resource.bitmap.CenterCrop
import com.bumptech.glide.load.resource.bitmap.RoundedCorners
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions
import com.bumptech.glide.request.RequestOptions
import com.bumptech.glide.request.target.DrawableImageViewTarget
import com.bumptech.glide.request.transition.Transition
import com.viaductecho.android.R

/**
 * Enhanced image loading utilities with proper error handling and optimization
 */
object ImageLoadingUtils {
    
    /**
     * Load image with enhanced error handling and smooth transitions
     */
    fun ImageView.loadImageEnhanced(
        url: String?,
        placeholder: Int = R.drawable.placeholder_article,
        error: Int = R.drawable.error_image,
        cornerRadius: Int = 0,
        onSuccess: (() -> Unit)? = null,
        onError: ((Exception?) -> Unit)? = null
    ) {
        val requestOptions = RequestOptions()
            .placeholder(placeholder)
            .error(error)
            .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            .skipMemoryCache(false)
        
        // Apply corner radius if specified
        val transformation = if (cornerRadius > 0) {
            RequestOptions().transform(CenterCrop(), RoundedCorners(cornerRadius))
        } else {
            RequestOptions().transform(CenterCrop())
        }
        
        val request = Glide.with(context)
            .load(url)
            .apply(requestOptions)
            .apply(transformation)
            .transition(DrawableTransitionOptions.withCrossFade(300))
            
        // Add listener only if callbacks are provided
        if (onSuccess != null || onError != null) {
            // Use simpler callback approach to avoid interface issues
            request.into(object : DrawableImageViewTarget(this) {
                override fun onResourceReady(resource: Drawable, transition: Transition<in Drawable>?) {
                    super.onResourceReady(resource, transition)
                    onSuccess?.invoke()
                }
                
                override fun onLoadFailed(errorDrawable: Drawable?) {
                    super.onLoadFailed(errorDrawable)
                    onError?.invoke(null)
                }
            })
        } else {
            request.into(this)
        }
    }
    
    /**
     * Load image with circular transformation
     */
    fun ImageView.loadCircularImage(
        url: String?,
        placeholder: Int = R.drawable.placeholder_article,
        error: Int = R.drawable.error_image
    ) {
        Glide.with(context)
            .load(url)
            .apply(
                RequestOptions()
                    .placeholder(placeholder)
                    .error(error)
                    .circleCrop()
                    .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
            )
            .transition(DrawableTransitionOptions.withCrossFade(300))
            .into(this)
    }
    
    /**
     * Preload image for better performance
     */
    fun preloadImage(context: android.content.Context, url: String?) {
        if (!url.isNullOrBlank()) {
            Glide.with(context)
                .load(url)
                .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
                .preload()
        }
    }
    
    /**
     * Clear image and free memory
     */
    fun ImageView.clearImage() {
        Glide.with(context).clear(this)
    }
}

