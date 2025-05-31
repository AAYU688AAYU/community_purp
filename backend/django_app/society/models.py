from django.db import models
from django.conf import settings

class Issue(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_issues')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='issues/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.issue.title} by {self.user.email}"

class Notice(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('maintenance', 'Maintenance'),
        ('event', 'Event'),
        ('emergency', 'Emergency'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='notices/', null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Meeting(models.Model):
    MEETING_TYPE_CHOICES = (
        ('general', 'General Body Meeting'),
        ('committee', 'Committee Meeting'),
        ('emergency', 'Emergency Meeting'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES)
    date = models.DateTimeField()
    duration = models.DurationField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_meetings')
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='meetings')
    meeting_link = models.URLField(null=True, blank=True)
    agenda = models.TextField()
    minutes = models.TextField(null=True, blank=True)
    recording_url = models.URLField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} on {self.date}"

class QRCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    purpose = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"QR Code for {self.user.email} - {self.purpose}"
