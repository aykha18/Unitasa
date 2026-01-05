import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock } from 'lucide-react';
import { Button } from '../ui';

interface ScheduledPost {
  id: string;
  content: string;
  platform: string;
  scheduled_at: string;
  status: 'pending' | 'posted' | 'failed';
}

interface CalendarViewProps {
  posts: ScheduledPost[];
  onDateClick: (date: Date) => void;
  onPostClick: (post: ScheduledPost) => void;
}

const CalendarView: React.FC<CalendarViewProps> = ({ posts, onDateClick, onPostClick }) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const changeMonth = (offset: number) => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + offset, 1));
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const monthName = currentDate.toLocaleString('default', { month: 'long' });
  const year = currentDate.getFullYear();

  const days = [];
  // Pad empty days
  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }
  // Add actual days
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(new Date(currentDate.getFullYear(), currentDate.getMonth(), i));
  }

  const getPostsForDate = (date: Date) => {
    return posts.filter(post => {
      const postDate = new Date(post.scheduled_at);
      return (
        postDate.getDate() === date.getDate() &&
        postDate.getMonth() === date.getMonth() &&
        postDate.getFullYear() === date.getFullYear()
      );
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Calendar Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <CalendarIcon className="w-5 h-5 mr-2 text-indigo-600" />
          {monthName} {year}
        </h2>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={() => changeMonth(-1)}>
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={() => changeMonth(1)}>
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Days Header */}
      <div className="grid grid-cols-7 border-b border-gray-200 bg-gray-50">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="p-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 auto-rows-fr">
        {days.map((date, index) => {
          if (!date) {
            return <div key={`empty-${index}`} className="min-h-[120px] bg-gray-50 border-b border-r border-gray-100 last:border-r-0" />;
          }

          const dayPosts = getPostsForDate(date);
          const isToday = new Date().toDateString() === date.toDateString();

          return (
            <div
              key={date.toISOString()}
              className={`min-h-[120px] p-2 border-b border-r border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer relative group ${
                isToday ? 'bg-indigo-50/30' : ''
              }`}
              onClick={() => onDateClick(date)}
            >
              <div className={`text-sm font-medium mb-1 flex justify-between items-center ${isToday ? 'text-indigo-600' : 'text-gray-700'}`}>
                <span className={isToday ? 'bg-indigo-100 px-2 py-0.5 rounded-full' : ''}>{date.getDate()}</span>
                {dayPosts.length > 0 && (
                  <span className="text-xs text-gray-400 font-normal">{dayPosts.length} posts</span>
                )}
              </div>
              
              <div className="space-y-1">
                {dayPosts.map(post => (
                  <div
                    key={post.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      onPostClick(post);
                    }}
                    className={`text-xs p-1.5 rounded border truncate cursor-pointer transition-shadow hover:shadow-sm flex items-center ${
                      post.status === 'posted' ? 'bg-green-50 border-green-100 text-green-700' :
                      post.status === 'failed' ? 'bg-red-50 border-red-100 text-red-700' :
                      'bg-white border-gray-200 text-gray-700'
                    }`}
                    title={post.content}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full mr-1.5 flex-shrink-0 ${
                      post.platform === 'twitter' ? 'bg-blue-400' :
                      post.platform === 'linkedin' ? 'bg-blue-700' :
                      post.platform === 'instagram' ? 'bg-pink-500' :
                      post.platform === 'facebook' ? 'bg-blue-600' : 'bg-gray-400'
                    }`} />
                    <span className="truncate">{post.content}</span>
                  </div>
                ))}
              </div>

              {/* Add Button (visible on hover) */}
              <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                 <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-lg leading-none pb-0.5 hover:bg-indigo-200">
                   +
                 </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CalendarView;
