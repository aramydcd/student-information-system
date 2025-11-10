print("Hey, how u doing?")

{% if enrollments %}
        <div class="row">
            {% for enrollment in enrollments %}
                <div class="col-md-4 mb-4">
                    <div class="card shadow-lg border-0 h-100 card-hover">
                        <div class="card-body">
                            <h5 class="card-title fw-bold">{{ enrollment.course.code }} - {{ enrollment.course.title }}</h5>
                            <p class="card-text text-muted">
                                Credit Units: <strong>{{ enrollment.course.credit_unit }}</strong><br>
                                Lecturer: <strong>{{ enrollment.course.lecturer.get_full_name|default:"N/A" }}</strong>
                            </p>
                            

                            <!-- Course Table -->
                            <h4 class="mt-5">🗓️ Attendance Details</h4>
                            <table class="table table-striped table-bordered mt-3">
                                <thead class="table-light">
                                    <tr>
                                        <th>Status</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for attendance in attendances %}
                                    <tr>
                                        <td>{{ attendance.present }}</td>
                                        <td>{{ attendance.date }}</td>
                                    </tr>
                                    {% empty %}
                                    <tr><td colspan="3" class="text-center text-muted">No courses yet.</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <p class="text-muted">You haven’t enrolled in any courses yet.</p>
    {% endif %}



{% load static %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<style>
  /* quick test style — temporary */
  .card-hover {
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    border-radius: 0.75rem;
  }
  .card-hover:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0,0,0,0.18);
    cursor: pointer;
  }
</style>
<div class="container py-4">
    <h2 class="mb-4 fw-bold text-primary">📚 Exam Eligibility</h2>

    <!-- Search Bar -->
    <form class="d-flex mb-3" method="GET">
        <input type="text" name="q" class="form-control me-2 shadow-sm" 
               placeholder="🔍 Filter by Course Code..." 
               value="{{ request.GET.q }}">
        <button class="btn btn-outline-primary shadow-sm">Filter</button>
    </form>


</div>
<div class="text-center mt-4">
    <a href="{% url 'home' %}" class="btn btn-lg btn-outline-primary shadow-sm px-4 py-2 rounded-pill">
        ⬅️ Back to Homepage
    </a>
</div>
{% endblock %}
