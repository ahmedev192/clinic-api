import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'ar';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  dir: 'ltr' | 'rtl';
}

const translations = {
  en: {
    'dashboard': 'Dashboard',
    'staff': 'Staff',
    'doctors': 'Doctors',
    'schedules': 'Schedules',
    'roles': 'Roles',
    'specializations': 'Specializations',
    'reports': 'Reports',
    'search': 'Search',
    'add_new': 'Add New',
    'edit': 'Edit',
    'delete': 'Delete',
    'save': 'Save',
    'cancel': 'Cancel',
    'total_staff': 'Total Staff',
    'total_doctors': 'Total Doctors',
    'active_staff': 'Active Staff',
    'available_doctors': 'Available Doctors',
    'name': 'Name',
    'role': 'Role',
    'status': 'Status',
    'contact': 'Contact',
    'actions': 'Actions',
    'active': 'Active',
    'inactive': 'Inactive',
    'view_schedule': 'View Schedule',
    'assign_role': 'Assign Role',
    'specialization': 'Specialization',
    'experience': 'Experience',
    'consultation_fee': 'Consultation Fee',
    'working_hours': 'Working Hours',
    'years': 'years',
  },
  ar: {
    'dashboard': 'لوحة التحكم',
    'staff': 'الموظفين',
    'doctors': 'الأطباء',
    'schedules': 'الجداول',
    'roles': 'الأدوار',
    'specializations': 'التخصصات',
    'reports': 'التقارير',
    'search': 'بحث',
    'add_new': 'إضافة جديد',
    'edit': 'تعديل',
    'delete': 'حذف',
    'save': 'حفظ',
    'cancel': 'إلغاء',
    'total_staff': 'إجمالي الموظفين',
    'total_doctors': 'إجمالي الأطباء',
    'active_staff': 'الموظفون النشطون',
    'available_doctors': 'الأطباء المتاحون',
    'name': 'الاسم',
    'role': 'الدور',
    'status': 'الحالة',
    'contact': 'جهة الاتصال',
    'actions': 'الإجراءات',
    'active': 'نشط',
    'inactive': 'غير نشط',
    'view_schedule': 'عرض الجدول',
    'assign_role': 'تعيين دور',
    'specialization': 'التخصص',
    'experience': 'الخبرة',
    'consultation_fee': 'رسوم الاستشارة',
    'working_hours': 'ساعات العمل',
    'years': 'سنوات',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations['en']] || key;
  };

  const dir = language === 'ar' ? 'rtl' : 'ltr';

  useEffect(() => {
    document.documentElement.dir = dir;
    document.documentElement.lang = language;
  }, [language, dir]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, dir }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
