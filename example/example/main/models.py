from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=250)

    def __unicode__(self):
        return self.title


class Ticket(models.Model):
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=250)
    description = models.TextField()
    file = models.FileField(upload_to='uploads/tickets/')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
