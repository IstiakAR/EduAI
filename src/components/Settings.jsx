import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, useUserId } from '../hooks/useAuth';
import { apiService } from '../services/apiService';

function Settings() {
  const { user } = useAuth();
  const userId = useUserId();
  const navigate = useNavigate();
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [userProfile, setUserProfile] = useState({
    display_name: '',
    school: '',
    preferences: {
      difficulty_preference: 'medium',
      exam_type_preference: 'mcq',
      notifications: true,
      auto_save: true
    }
  });
  
  const [originalProfile, setOriginalProfile] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Load user profile on mount
  useEffect(() => {
    if (userId) {
      loadUserProfile();
    }
  }, [userId]);

  // Check for changes whenever profile is updated
  useEffect(() => {
    if (originalProfile) {
      const changes = JSON.stringify(userProfile) !== JSON.stringify(originalProfile);
      setHasChanges(changes);
    }
  }, [userProfile, originalProfile]);

  const loadUserProfile = async () => {
    try {
      setIsLoading(true);
      console.log('Loading user profile for:', userId);
      
      const profile = await apiService.getUserProfile(userId);
      console.log('Loaded profile:', profile);
      
      if (profile) {
        setUserProfile(profile);
        setOriginalProfile(profile);
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePreferenceChange = (preference, value) => {
    setUserProfile(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [preference]: value
      }
    }));
  };

  const saveProfile = async () => {
    if (!userId || !hasChanges) return;
    
    try {
      setIsSaving(true);
      console.log('Saving profile:', userProfile);
      
      await apiService.updateUserProfile(userId, userProfile);
      setOriginalProfile({ ...userProfile });
      setHasChanges(false);
      
      console.log('Profile saved successfully');
    } catch (error) {
      console.error('Failed to save profile:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const resetChanges = () => {
    if (originalProfile) {
      setUserProfile({ ...originalProfile });
      setHasChanges(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-100 flex">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
              <p className="text-sm text-gray-600 mt-1">Manage your account preferences and information</p>
            </div>
            
            <div className="flex items-center gap-2">
              {hasChanges && (
                <>
                  <button
                    onClick={resetChanges}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                  >
                    Reset
                  </button>
                  <button
                    onClick={saveProfile}
                    disabled={isSaving}
                    className="px-4 py-2 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50"
                  >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </>
              )}
              
              <button
                onClick={() => navigate('/chat')}
                className="ml-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                title="Back to Chat"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>        {/* Settings Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-2xl mx-auto space-y-8">
            
            {/* Profile Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={userProfile.display_name}
                    onChange={(e) => handleInputChange('display_name', e.target.value)}
                    placeholder="Enter your display name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">This is how your name will appear to others</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    School / Institution
                  </label>
                  <input
                    type="text"
                    value={userProfile.school}
                    onChange={(e) => handleInputChange('school', e.target.value)}
                    placeholder="Enter your school or institution"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Optional: Your educational institution</p>
                </div>
              </div>
            </div>

            {/* Exam Preferences */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Exam Preferences</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Difficulty Level
                  </label>
                  <select
                    value={userProfile.preferences.difficulty_preference}
                    onChange={(e) => handlePreferenceChange('difficulty_preference', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Your preferred difficulty level for new exams</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Exam Type
                  </label>
                  <select
                    value={userProfile.preferences.exam_type_preference}
                    onChange={(e) => handlePreferenceChange('exam_type_preference', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  >
                    <option value="mcq">Multiple Choice (MCQ)</option>
                    <option value="written">Written/Essay</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">Your preferred exam format</p>
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Account Information</h2>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Email:</span>
                  <span className="font-medium text-gray-900">{user?.email || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Account Created:</span>
                  <span className="text-gray-900">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
