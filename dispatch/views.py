from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.forms import inlineformset_factory
from .models import Dispatch, Load
from .forms import DispatchForm, LoadForm
from truck.models import Vehicle, Compartment
from fuelstation.models import FuelStation

class DispatchListView(LoginRequiredMixin, ListView):
    model = Dispatch
    template_name = 'dispatch/dispatch_list.html'
    context_object_name = 'dispatches'
    paginate_by = 10

    def get_queryset(self):
        # Use raw SQL to get dispatches with station names
        from django.db import connection

        # Start with the base query
        query = "SELECT d.id, d.dispatch_date, d.status, v.license_plate, fs.name as station_name, "
        query += "d.notes, d.driver_id, d.vehicle_id, d.fuel_station_id "
        query += "FROM dispatch_dispatch d "
        query += "LEFT JOIN truck_vehicle v ON d.vehicle_id = v.id "
        query += "LEFT JOIN fuelstation_fuelstation fs ON d.fuel_station_id = fs.id "

        # Add filters
        where_clauses = []
        params = []

        status_filter = self.request.GET.get('status')
        if status_filter:
            where_clauses.append("d.status = ?")
            params.append(status_filter)

        search_query = self.request.GET.get('search')
        if search_query:
            where_clauses.append("(v.license_plate LIKE ? OR fs.name LIKE ?)")
            params.append(f'%{search_query}%')
            params.append(f'%{search_query}%')

        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses)

        # Add ordering
        query += " ORDER BY d.dispatch_date DESC"

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            dispatches_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Create a custom queryset
        from django.db.models.query import QuerySet
        queryset = QuerySet(model=Dispatch)
        queryset._result_cache = []

        # Create Dispatch objects with station_name attribute
        for data in dispatches_data:
            dispatch = Dispatch(id=data['id'],
                               dispatch_date=data['dispatch_date'],
                               status=data['status'],
                               notes=data['notes'])

            # Set the vehicle and fuel_station IDs
            dispatch.vehicle_id = data['vehicle_id']
            dispatch.fuel_station_id = data['fuel_station_id']
            dispatch.driver_id = data['driver_id']

            # Add custom attributes
            dispatch.vehicle_license_plate = data['license_plate']
            dispatch.station_name = data['station_name']

            queryset._result_cache.append(dispatch)

        return queryset

class DispatchDetailView(LoginRequiredMixin, DetailView):
    model = Dispatch
    template_name = 'dispatch/dispatch_detail.html'
    context_object_name = 'dispatch'

@login_required
def add_or_edit_dispatch(request, pk=None):
    LoadFormset = inlineformset_factory(
        Dispatch, Load,
        form=LoadForm,
        extra=1,
        can_delete=True
    )

    if pk:
        dispatch = get_object_or_404(Dispatch, pk=pk)
    else:
        dispatch = None

    if request.method == 'POST':
        form = DispatchForm(request.POST, instance=dispatch)
        formset = LoadFormset(request.POST, instance=dispatch)

        if form.is_valid() and formset.is_valid():
            dispatch_obj = form.save(commit=False)
            if not dispatch:  # Nëse është një dispatch i ri
                dispatch_obj.created_by = request.user
            dispatch_obj.save()

            formset.instance = dispatch_obj
            formset.save()

            messages.success(request, 'Dispeçi u ruajt me sukses!')
            return redirect('dispatch:dispatch_list')
        else:
            messages.error(request, 'Ju lutemi korrigjoni gabimet e mëposhtme.')
    else:
        form = DispatchForm(instance=dispatch)
        formset = LoadFormset(instance=dispatch)

    return render(request, 'dispatch/dispatch_form.html', {
        'form': form,
        'formset': formset,
        'dispatch': dispatch
    })

@login_required
def update_dispatch_status(request, pk, status):
    dispatch = get_object_or_404(Dispatch, pk=pk)

    # Verifikoni nëse statusi është valid
    if status in [choice[0] for choice in Dispatch.STATUS_CHOICES]:
        old_status = dispatch.get_status_display()
        dispatch.status = status

        # Përditësoni datat sipas statusit
        if status == 'IN_PROGRESS' and not dispatch.arrival_date:
            from django.utils import timezone
            dispatch.arrival_date = timezone.now()
        elif status == 'COMPLETED' and not dispatch.completion_date:
            from django.utils import timezone
            dispatch.completion_date = timezone.now()

        dispatch.save()
        messages.success(request, f'Statusi i dispeçit u ndryshua nga "{old_status}" në "{dispatch.get_status_display()}".')
    else:
        messages.error(request, 'Statusi i zgjedhur nuk është valid.')

    return redirect('dispatch:dispatch_detail', pk=pk)

@login_required
def delete_dispatch(request, pk):
    dispatch = get_object_or_404(Dispatch, pk=pk)

    if request.method == 'POST':
        dispatch.delete()
        messages.success(request, 'Dispeçi u fshi me sukses!')
        return redirect('dispatch:dispatch_list')

    return render(request, 'dispatch/dispatch_confirm_delete.html', {'dispatch': dispatch})
