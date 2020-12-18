
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r"projects", viewset=ProjectModelViewSet, basename="projects")
router.register(r"datasets", viewset=DatasetModelViewSet, basename="datasets")
router.register(r"predictors", viewset=PredictorModelViewSet, basename="predictors")
router.register(r"forecasts", viewset=ForecastModelViewSet, basename="forecasts")
router.register(
    r"evaluations", viewset=EvaluationResultModelViewSet, basename="evaluation_results"
)
router.register(
    r"dataset-import-jobs",
    viewset=DatasetImportJobModelViewSet,
    basename="dataset_import_jobs",
)
router.register(
    r"training-jobs", viewset=TrainingJobModelViewSet, basename="training_jobs"
)
router.register(
    r"forecast-jobs", viewset=ForecastJobModelViewSet, basename="forecast_jobs"
)

urlpatterns = [
    path("", include(router.urls)),
    re_path(r"^datasets/(?P<dataset_id>\d+)/upload", UploadDataView.as_view()),
    re_path(r"^predictors/(?P<predictor_id>\d+)/start", TrainingJobView.as_view()),
    re_path(
        r"^predictors/(?P<predictor_id>\d+)/evaluation-result",
        EvaluationResultView.as_view(),
    ),
    re_path(r"^forecasts/(?P<forecast_id>\d+)/start", ForecastJobViewStart.as_view()),
    re_path(
        r"^forecasts/(?P<forecast_id>\d+)/download", ForecastJobViewDownload.as_view()
    ),
    path(r"available-predictors", AvailablePredictorsView.as_view()),
]
