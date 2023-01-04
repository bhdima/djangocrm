from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views import generic
from .models import Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganizorAndLoginRequiredMixin
# Create your views here.

#CRUD+L - Create, Retrieve, Update, and Delete + List
#Django generic views are also structured like crud

#class based views elimate code that we right over and over


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")
        




class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'



#This is a view(based function)
def landing_page(request):
    return render(request, "landing.html")


# #converting the lead_list function based view to a class based view
class LeadListView(generic.ListView):
    #specifying a template name
    template_name = "leads/lead_list.html"
    #ListView automatically assign context variable to be object_list
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizor:
            queryset = Lead.objects.filter(
                organization=user.userprofile,
                agent__isnull=False
                )
        #filtering the leads based on the conditions of the user
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization,
                agent__isnull=False
                )
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizor:
            queryset = Lead.objects.filter(
                organization=user.userprofile,
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context


#django takes our function and passes request into it and returns our httpresponse
def lead_list(request):
    #retrieved all leads with a queryset
    leads = Lead.objects.all()
    #context gets passed into render method, and the template makes use of this information 
    context = {
        "leads": leads
    }
    #return HttpResponse("Hello World")
    #sending back html templates
    return render(request, "leads/lead_list.html", context)


class LeadDetailView(generic.DetailView):
    template_name = "leads/lead_detail.html"
    queryset = Lead.objects.all()
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizor:
            queryset = Lead.objects.filter(organization=user.userprofile)
        #filtering the leads based on the conditions of the user
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset
    


def lead_detail(request, pk):
    #retrieving a specific row in object manager
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    return render(request, "leads/lead_detail.html", context)




class LeadCreateView(OrganizorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)



#this view will allow us to submit a form and create our own lead
def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        #checking if the data passed into form is valid
        if form.is_valid():
            #this call does the same thing that the commented model does
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
    return render(request, "leads/lead_create.html", context)


#updating a existing lead
class LeadUpdateView(OrganizorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    queryset = Lead.objects.all()

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organization
        #filtering the leads based on the conditions of the user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")



def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, "leads/lead_update.html", context)


class LeadDeleteView(OrganizorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"


    def get_success_url(self):
        return reverse("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organization
        #filtering the leads based on the conditions of the user
        return Lead.objects.filter(organization=user.userprofile)



def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganizorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm


    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update ({
            "request": self.request
        })
        return kwargs


    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        #accessing value that is submitted
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizor:
            queryset = Lead.objects.filter(
                organization=user.userprofile
                )
        #filtering the leads based on the conditions of the user
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
                )
        
        context.update({
            "unassigned_lead_count": Lead.objects.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizor:
            queryset = Category.objects.filter(
                organization=user.userprofile
                )
        #filtering the leads based on the conditions of the user
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
                )
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"


    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizor:
            queryset = Category.objects.filter(
                organization=user.userprofile
                )
        #filtering the leads based on the conditions of the user
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
                )
        return queryset


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("catetory:category-list")







#updating a existing lead
class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm



    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizor:
            queryset = Lead.objects.filter(organization=user.userprofile)
        #filtering the leads based on the conditions of the user
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})






class CategoryDeleteView(OrganizorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/category_delete.html"


    def get_success_url(self):
        return reverse("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organization
        #filtering the leads based on the conditions of the user
        return Category.objects.filter(organization=user.userprofile)






# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         #checking if the data passed into form is valid
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             return redirect("/leads")
#     context = {
#         "form": form,
#         "lead": lead
#     }
#     return render(request, "leads/lead_update.html", context)





# def lead_create(request):
#     form = LeadModelForm()
#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         #checking if the data passed into form is valid
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             agent = Agent.objects.first()
#             Lead.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 age=age,
#                 agent=agent
#             )
#             return redirect("/leads")
#     context = {
#         "form": form
#     }
#     return render(request, "leads/lead_create.html", context)