import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'ar';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  isRTL: boolean;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    patients: 'Patients',
    'patients-list': 'Patients List',
    'add-patient': 'Add Patient',
    'medical-history': 'Medical History',
    documents: 'Documents',
    'audit-logs': 'Audit Logs',
    settings: 'Settings',
    logout: 'Logout',

    // Dashboard
    'total-patients': 'Total Patients',
    'active-patients': 'Active Patients',
    'inactive-patients': 'Inactive Patients',
    'new-registrations': 'New Registrations',
    'male-patients': 'Male Patients',
    'female-patients': 'Female Patients',
    'gender-distribution': 'Gender Distribution',
    'patient-statistics': 'Patient Statistics',
    'recent-activity': 'Recent Activity',

    // Patients
    name: 'Name',
    'name-en': 'Name (English)',
    'name-ar': 'Name (Arabic)',
    phone: 'Phone',
    gender: 'Gender',
    status: 'Status',
    actions: 'Actions',
    search: 'Search',
    'search-patients': 'Search patients...',
    view: 'View',
    edit: 'Edit',
    delete: 'Delete',
    'no-patients': 'No patients found',
    male: 'Male',
    female: 'Female',
    active: 'Active',
    inactive: 'Inactive',
    
    // Patient Form
    'patient-information': 'Patient Information',
    'first-name': 'First Name',
    'last-name': 'Last Name',
    'date-of-birth': 'Date of Birth',
    email: 'Email',
    'national-id': 'National ID',
    'blood-type': 'Blood Type',
    city: 'City',
    address: 'Address',
    'emergency-contact': 'Emergency Contact',
    'emergency-phone': 'Emergency Phone',
    save: 'Save',
    cancel: 'Cancel',
    'required-field': 'This field is required',

    // Patient Profile
    'personal-info': 'Personal Information',
    allergies: 'Allergies',
    'chronic-conditions': 'Chronic Conditions',
    'patient-details': 'Patient Details',
    age: 'Age',
    'years-old': 'years old',
    
    // Medical History
    date: 'Date',
    diagnosis: 'Diagnosis',
    treatment: 'Treatment',
    notes: 'Notes',
    'add-history': 'Add History',
    
    // Documents
    'document-name': 'Document Name',
    'upload-date': 'Upload Date',
    verified: 'Verified',
    verify: 'Verify',
    unverify: 'Unverify',
    download: 'Download',
    'upload-document': 'Upload Document',
    'drag-drop': 'Drag and drop files here or click to upload',
    
    // Common
    loading: 'Loading...',
    'error-occurred': 'An error occurred',
    'success': 'Success',
    'confirm-delete': 'Are you sure you want to delete this?',
    yes: 'Yes',
    no: 'No',
    close: 'Close',
    'select-option': 'Select an option',
  },
  ar: {
    // Navigation
    dashboard: 'لوحة التحكم',
    patients: 'المرضى',
    'patients-list': 'قائمة المرضى',
    'add-patient': 'إضافة مريض',
    'medical-history': 'التاريخ الطبي',
    documents: 'المستندات',
    'audit-logs': 'سجلات التدقيق',
    settings: 'الإعدادات',
    logout: 'تسجيل الخروج',

    // Dashboard
    'total-patients': 'إجمالي المرضى',
    'active-patients': 'المرضى النشطون',
    'inactive-patients': 'المرضى غير النشطين',
    'new-registrations': 'التسجيلات الجديدة',
    'male-patients': 'المرضى الذكور',
    'female-patients': 'المرضى الإناث',
    'gender-distribution': 'توزيع الجنس',
    'patient-statistics': 'إحصائيات المرضى',
    'recent-activity': 'النشاط الأخير',

    // Patients
    name: 'الاسم',
    'name-en': 'الاسم (بالإنجليزية)',
    'name-ar': 'الاسم (بالعربية)',
    phone: 'الهاتف',
    gender: 'الجنس',
    status: 'الحالة',
    actions: 'الإجراءات',
    search: 'بحث',
    'search-patients': 'البحث عن المرضى...',
    view: 'عرض',
    edit: 'تعديل',
    delete: 'حذف',
    'no-patients': 'لم يتم العثور على مرضى',
    male: 'ذكر',
    female: 'أنثى',
    active: 'نشط',
    inactive: 'غير نشط',
    
    // Patient Form
    'patient-information': 'معلومات المريض',
    'first-name': 'الاسم الأول',
    'last-name': 'اسم العائلة',
    'date-of-birth': 'تاريخ الميلاد',
    email: 'البريد الإلكتروني',
    'national-id': 'الرقم الوطني',
    'blood-type': 'فصيلة الدم',
    city: 'المدينة',
    address: 'العنوان',
    'emergency-contact': 'جهة اتصال الطوارئ',
    'emergency-phone': 'هاتف الطوارئ',
    save: 'حفظ',
    cancel: 'إلغاء',
    'required-field': 'هذا الحقل مطلوب',

    // Patient Profile
    'personal-info': 'المعلومات الشخصية',
    allergies: 'الحساسية',
    'chronic-conditions': 'الأمراض المزمنة',
    'patient-details': 'تفاصيل المريض',
    age: 'العمر',
    'years-old': 'سنة',
    
    // Medical History
    date: 'التاريخ',
    diagnosis: 'التشخيص',
    treatment: 'العلاج',
    notes: 'ملاحظات',
    'add-history': 'إضافة سجل طبي',
    
    // Documents
    'document-name': 'اسم المستند',
    'upload-date': 'تاريخ الرفع',
    verified: 'موثق',
    verify: 'توثيق',
    unverify: 'إلغاء التوثيق',
    download: 'تحميل',
    'upload-document': 'رفع مستند',
    'drag-drop': 'اسحب وأفلت الملفات هنا أو انقر للرفع',
    
    // Common
    loading: 'جاري التحميل...',
    'error-occurred': 'حدث خطأ',
    'success': 'نجح',
    'confirm-delete': 'هل أنت متأكد من الحذف؟',
    yes: 'نعم',
    no: 'لا',
    close: 'إغلاق',
    'select-option': 'اختر خياراً',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('language') as Language;
    return saved || 'en';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        isRTL: language === 'ar',
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
