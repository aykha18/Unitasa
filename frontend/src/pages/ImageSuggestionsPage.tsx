import React, { useState } from 'react';
import { Image, Search, Download, Heart, Share2, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui';
import { aiContentHubService, ImageSuggestion } from '../services/aiContentHubService';

const ImageSuggestionsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [images, setImages] = useState<ImageSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ImageSuggestion | null>(null);
  const [error, setError] = useState<string | null>(null);


  const searchImages = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await aiContentHubService.generateImages({
        query: searchQuery.trim(),
        count: 12
      });

      setImages(response.images);
    } catch (err) {
      console.error('Failed to generate images:', err);
      setError('Failed to generate images. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = async (image: ImageSuggestion) => {
    try {
      // In a real implementation, this would download the image
      // For now, we'll just open it in a new tab
      window.open(image.download_url || image.url, '_blank');
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  const shareImage = async (image: ImageSuggestion) => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: image.title,
          text: `Check out this image: ${image.title}`,
          url: image.download_url || image.url
        });
      } else {
        // Fallback: copy URL to clipboard
        await navigator.clipboard.writeText(image.download_url || image.url);
        alert('Image URL copied to clipboard!');
      }
    } catch (error) {
      console.error('Error sharing image:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <Image className="w-8 h-8 text-green-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Image Suggestions</h1>
          </div>
          <p className="text-gray-600 text-lg">
            Find the perfect images to enhance your social media content and marketing campaigns
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for images (e.g., business, technology, marketing, AI)"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                onKeyPress={(e) => e.key === 'Enter' && searchImages()}
              />
            </div>
            <Button
              onClick={searchImages}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 disabled:opacity-50 px-6"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>

          {/* Popular Tags */}
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Popular searches:</p>
            <div className="flex flex-wrap gap-2">
              {['business', 'technology', 'marketing', 'AI', 'team', 'office', 'growth', 'analytics'].map((tag) => (
                <button
                  key={tag}
                  onClick={() => setSearchQuery(tag)}
                  className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Image Grid */}
        {images.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {images.map((image) => (
              <div
                key={image.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedImage(image)}
              >
                <div className="aspect-video relative">
                  <img
                    src={image.thumbnail_url}
                    alt={image.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-opacity flex items-center justify-center">
                    <div className="opacity-0 hover:opacity-100 flex space-x-2">
                      <Button
                        onClick={() => downloadImage(image)}
                        size="sm"
                        variant="secondary"
                        className="bg-white/90 hover:bg-white"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button
                        onClick={() => shareImage(image)}
                        size="sm"
                        variant="secondary"
                        className="bg-white/90 hover:bg-white"
                      >
                        <Share2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="p-4">
                  <h3 className="font-medium text-gray-900 mb-1">{image.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">Source: {image.source}</p>
                  <div className="flex flex-wrap gap-1">
                    {image.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    {image.width} × {image.height}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-green-600" />
            <p className="text-gray-600">Searching for perfect images...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && images.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <Image className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No images found
            </h3>
            <p className="text-gray-600 mb-4">
              Try searching with different keywords or browse popular categories.
            </p>
            <Button onClick={() => searchImages()} className="bg-green-600 hover:bg-green-700">
              Try Popular Search
            </Button>
          </div>
        )}

        {/* Image Modal */}
        {selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedImage.title}</h3>
                  <p className="text-sm text-gray-600">Source: {selectedImage.source}</p>
                </div>
                <Button
                  onClick={() => setSelectedImage(null)}
                  variant="outline"
                  size="sm"
                >
                  ✕
                </Button>
              </div>

              <div className="p-4">
                <img
                  src={selectedImage.url}
                  alt={selectedImage.title}
                  className="w-full h-auto max-h-96 object-contain mx-auto mb-4"
                />

                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedImage.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="flex space-x-3">
                  <Button
                    onClick={() => downloadImage(selectedImage)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                  <Button
                    onClick={() => shareImage(selectedImage)}
                    variant="outline"
                  >
                    <Share2 className="w-4 h-4 mr-2" />
                    Share
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Usage Tips */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <div className="flex items-start">
            <Image className="w-6 h-6 text-blue-600 mr-3 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-2">Image Best Practices</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use high-quality images (at least 1200x675px for best results)</li>
                <li>• Choose images that match your brand colors and style</li>
                <li>• Ensure images are relevant to your content and audience</li>
                <li>• Consider aspect ratios: 1:1 for Instagram, 16:9 for other platforms</li>
                <li>• Always check image rights and usage permissions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageSuggestionsPage;