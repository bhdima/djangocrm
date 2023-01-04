import random
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, render, redirect
from leads.models import Agent
from .forms import AgentModelForm
from .mixins import OrganizorAndLoginRequiredMixin


# Create your views here.
class AgentListView(OrganizorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"

    def get_queryset(self):
        organization = self.request.user.userprofile
        #filtering by organiztion for the request.user.profile model
        return Agent.objects.filter(organization=organization)




#def agent_list(request):
#     agents = Agent.objects.all()
#     context = {
#         "agents": agents
#     }
#     return render(request, "leads/agent_list.html", context)




class AgentCreateView(OrganizorAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm
    
    def get_success_url(self):
        return reverse("agents:agent-list")

    #overiding the form validation method and passing in organization
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organizor = False
        user.set_password(f"{random.randint(0, 10000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        send_mail(
            subject="You are invited to be a agent",
            message="You were added as an agent on DJCRM. Please come login to start working.",
            from_email="admin@test.com",
            recipient_list=[user.email]
        )
        # agent.organization = self.request.user.userprofile
        # agent.save()
        return super(AgentCreateView, self).form_valid(form)



# def agent_create(request):
    # form = AgentModelForm()
    # if request.method == "POST":
    #     form = AgentModelForm(request.POST)
    #     #checking if the data passed into form is valid
    #     if form.is_valid():
    #         #this call does the same thing that the commented model does
    #         form.save()
    #         return redirect("/agents")
    # context = {
    #     "form": form
    # }
    # return render(request, "agents/agent_create.html", context)



# def agent_list(request):
    # agents = Agent.objects.all()
    # context = {
    #     "agents": agents
    # }
    # return render(request, "leads/agent_list.html", context)

class AgentDetailView(OrganizorAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)




# def agent_detail(request, pk):
    # #retrieving a specific row in object manager
    # agent = Agent.objects.get(id=pk)
    # context = {
    #     "agent": agent
    # }
    # return render(request, "agents/agent_detail.html", context)




class AgentUpdateView(OrganizorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)




# def agent_update(request, pk):
#     agent = Agent.objects.get(id=pk)
#     form = AgentModelForm(instance=agent)
#     if request.method == "POST":
#         form = AgentModelForm(request.POST, instance=agent)
#         if form.is_valid():
#             form.save()
#             return redirect("/agents")
#     context = {
#         "form": form,
#         "agent": agent
#     }
#     return render(request, "agents/agent_update.html", context)




class AgentDeleteView(OrganizorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)




# def agent_delete(request, pk):
#     agent = Agent.objects.get(id=pk)
#     agent.delete()
#     return redirect("/leads")